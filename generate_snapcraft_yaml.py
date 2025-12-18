import re
import jinja2
import subprocess
from launchpadlib.launchpad import Launchpad


lp = Launchpad.login_anonymously("snap-build", "production", version="devel")
ubuntu = lp.distributions["ubuntu"]
archive = ubuntu.main_archive

# For each active base, find the latest published version of the binary
base_re = re.compile("^core\d*$")
for base in lp.snap_bases:
    # core should be used for xenial rather than core16
    if base_re.match(base.name) is None or base.name == "core16":
        continue

    series = base.distro_series
    if not series.active:
        continue

    # Get the newest published version of the binary
    pubs = archive.getPublishedBinaries(
        binary_name="libsecret-tools",
        exact_match=True,
        distro_arch_series=series.getDistroArchSeries(archtag="amd64"),
        #pocket="Security",
        status="Published",
        ordered=False,  # faster; set True if you need deterministic ordering
    )
    if not pubs:
        print("No published packages found")
        continue

    newest = sorted(pubs, key=lambda p: (p.date_published or ""), reverse=True)[0]
    version = newest.binary_package_version

    # Generate the snapcraft.yaml file
    with open("snapcraft.jinja2") as fd:
        snapcraft_template = jinja2.Template(fd.read())
    snapcraft = snapcraft_template.render(base=base.name, release=series.name, version=version)

    # Change branch, save the snapcraft.yaml and commit
    p = subprocess.run(["git", "checkout", series.name])
    if p.returncode != 0:
        p = subprocess.run(["git", "checkout", "-b", series.name])
    with open("snap/snapcraft.yaml", "w") as fd:
        fd.write(snapcraft)
    subprocess.run(["git", "add", "snap/snapcraft.yaml"])
    subprocess.run(["git", "commit", "-m", f"update libsecret-tools to {version} on {series.name}"])
    subprocess.run(["git", "checkout", "master"])
