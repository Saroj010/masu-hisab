"""Finish the Capacitor Android project: icons, camera permission, version and signing.
Run from the repository root after `npx cap add android` and `npx cap sync android`."""
import os, re, shutil

A = 'app/android/app'
build = os.environ.get('GITHUB_RUN_NUMBER', '1')

# 1. app icons
for root, dirs, files in os.walk('app/res'):
    for f in files:
        src = os.path.join(root, f)
        dst = os.path.join(A, 'src/main', os.path.relpath(src, 'app'))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)

# 2. camera permission for taking photos inside the app
man = os.path.join(A, 'src/main/AndroidManifest.xml')
m = open(man, encoding='utf-8').read()
if 'android.permission.CAMERA' not in m:
    m = m.replace('<uses-permission android:name="android.permission.INTERNET" />',
                  '<uses-permission android:name="android.permission.INTERNET" />\n'
                  '    <uses-permission android:name="android.permission.CAMERA" />\n'
                  '    <uses-feature android:name="android.hardware.camera" android:required="false" />')
    assert 'android.permission.CAMERA' in m, 'could not add camera permission'
open(man, 'w', encoding='utf-8').write(m)

# 3. version and signing (the password comes from the KS_PASS repository secret)
g = os.path.join(A, 'build.gradle')
s = open(g, encoding='utf-8').read()
s, n1 = re.subn(r'versionCode \d+', 'versionCode ' + build, s)
s, n2 = re.subn(r'versionName "[^"]*"', 'versionName "1.' + build + '"', s)
assert n1 == 1 and n2 == 1, 'version lines not found'
signing = '''    signingConfigs {
        release {
            storeFile file(System.getenv("KS_FILE"))
            storePassword System.getenv("KS_PASS")
            keyAlias "masuhisab"
            keyPassword System.getenv("KS_PASS")
            storeType "pkcs12"
        }
    }
    buildTypes {'''
assert s.count('    buildTypes {') == 1, 'buildTypes not found'
s = s.replace('    buildTypes {', signing, 1)
s, n3 = re.subn(r'(release \{\s*\n\s*minifyEnabled false)', r'\1\n            signingConfig signingConfigs.release', s)
assert n3 == 1, 'release block not found'
open(g, 'w', encoding='utf-8').write(s)

# 4. stamp the build number into the app so it can tell when a newer version exists
idx = os.path.join(A, 'src/main/assets/public/index.html')
h = open(idx, encoding='utf-8').read()
assert '__MASU_BUILD__' in h, 'build placeholder missing'
open(idx, 'w', encoding='utf-8').write(h.replace('__MASU_BUILD__', build))
print('android project ready, build', build)
