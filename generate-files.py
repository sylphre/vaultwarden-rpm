import os
import re
import time

from github3 import login as ghlogin

# Keeps the two spec files in sync with the latest upstream releases:
# bumps Version, resets Release to 1, prepends a %changelog entry, and
# re-points the server's web vault dependency.

PACKAGER = 'Laurier Sylph. <laurier@sylph.re>'

SERVER_SPEC = 'vaultwarden/rpm/vaultwarden.spec'
WEB_SPEC = 'vaultwarden-web-vault/rpm/vaultwarden-web-vault.spec'

github = ghlogin('', '', os.environ['GITHUB_TOKEN'])

# latest version of vaultwarden
server_repository = github.repository('dani-garcia', 'vaultwarden')
server_release = server_repository.latest_release()
server_version = server_release.tag_name
server_version_clean = server_version.replace('v', '')

# latest version of bw_web_builds
web_repository = github.repository('dani-garcia', 'bw_web_builds')
web_release = web_repository.latest_release()
web_version = web_release.tag_name
web_version_clean = web_version.replace('v', '')

# timestamp for the rpm changelog: "Sat Jul 25 2026", no zero-padded day
release_date = '%s %s %d %s' % (time.strftime('%a'), time.strftime('%b'),
                                int(time.strftime('%d')), time.strftime('%Y'))


print('Latest upstream server release: %s' % server_version_clean)
print('Latest upstream web vault release: %s' % web_version_clean)


def read_spec_version(spec):
    """Return (text, version, release) as written in the spec file."""
    with open(spec, 'r') as f:
        text = f.read()
    version = re.search(r'^Version:\s*(\S+)$', text, re.M)
    release = re.search(r'^Release:\s*([0-9]+)', text, re.M)
    assert version and release, 'cannot parse %s' % spec
    return text, version.group(1), release.group(1)


def bump_spec(spec, text, new_version, changelog_lines):
    """Set Version, reset Release to 1 and prepend a %changelog entry."""
    text = re.sub(r'^Version:(\s*)\S+$', r'Version:\g<1>%s' % new_version,
                  text, count=1, flags=re.M)
    text = re.sub(r'^Release:(\s*)[0-9]+', r'Release:\g<1>1',
                  text, count=1, flags=re.M)

    entry = '* %s %s - %s-1\n' % (release_date, PACKAGER, new_version)
    entry += ''.join('- %s\n' % line for line in changelog_lines)
    text = text.replace('%changelog\n', '%changelog\n' + entry + '\n', 1)

    with open(spec, 'w') as f:
        f.write(text)


any_updates = False

# update web vault spec
web_text, current_web_version, current_web_release = read_spec_version(WEB_SPEC)
web_version_rpm = '%s-%s' % (current_web_version, current_web_release)
print('vaultwarden-web-vault: current version %s' % current_web_version)
if current_web_version != web_version_clean:
    any_updates = True
    print('Web vault needs update')
    bump_spec(WEB_SPEC, web_text, web_version_clean,
              ['Update to upstream version %s.' % web_version])

    # set rpm version
    web_version_rpm = '%s-1' % web_version_clean


# update server spec
server_text, current_server_version, current_server_release = read_spec_version(SERVER_SPEC)
server_version_rpm = '%s-%s' % (current_server_version, current_server_release)
print('vaultwarden: current version %s' % current_server_version)
if current_server_version != server_version_clean:
    any_updates = True
    print('Server needs update')

    # require the latest web vault version
    server_text = re.sub(r'^%global vw_web_version\s+\S+$',
                         '%%global vw_web_version %s' % web_version_clean,
                         server_text, count=1, flags=re.M)

    bump_spec(SERVER_SPEC, server_text, server_version_clean,
              ['Update to upstream version %s.' % server_version,
               'Require web vault version %s.' % web_version])

    # set rpm version
    server_version_rpm = '%s-1' % server_version_clean


# write GitHub environment variables
with open(os.getenv('GITHUB_ENV', 'github.env'), 'w') as f:
    f.write('VW_SERVER_VERSION=%s\n' % server_version)
    f.write('VW_WEB_VERSION=%s\n' % web_version)
    f.write('VW_SERVER_VERSION_CLEAN=%s\n' % server_version_clean)
    f.write('VW_WEB_VERSION_CLEAN=%s\n' % web_version_clean)
    f.write('VW_SERVER_VERSION_RPM=%s\n' % server_version_rpm)
    f.write('VW_WEB_VERSION_RPM=%s\n' % web_version_rpm)
    if any_updates:
        f.write('VW_HAS_UPDATE=true\n')
