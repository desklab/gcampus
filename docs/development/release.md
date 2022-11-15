# Release

### Unstable versions / Staging environment

Potentially unstable versions should be deployed to the staging
environment ([dev.gewaessercampus.de](https://dev.gewaessercampus.de)) first. Make sure to tag them
accordingly (`alpha`, `beta`, `rc`) and set the checkbox for pre-release in the GitHub UI.

### Pre-Release-Checks

Make sure to check the following list before releasing a new major or minor version. You can use the fixture to import a
dataset covering different combinations of courses, access keys, parameters, measurements, etc. into your local
environment.

- Check that the testsuite is passing.
- Check that translations are up-to-date.
- Check that all of the following actions work as intended.
    - Use the map to explore all measurements.
    - Register a new course.
    - Login & Logout with a course token.
    - Login & Logout with an access key.
    - Manage the access keys of a course through the course administration page.
    - Create a new measurement.
    - Edit an existing measurement.
    - Use a calibration to convert Optical Density to concentration.
    - Filter the list of measurements.
    - Filter the list of waters.
    - Download a measurement detail document.
    - Download a measurement list document.
    - Download a csv summary from the list of measurements.

### Creating a new release

Then follow these steps to create a new release:

- Update version in `gcampus/__init__.py`
- Create git tag with version.
- Commit and push to remote (including the tag).
- Use the GitHub UI to create a release.
- Wait for the Actions to complete, then check that deployment was successful.
