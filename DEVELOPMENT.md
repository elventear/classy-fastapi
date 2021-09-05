# Releases

Releases are built and pushed to PyPi by the CI. A release is triggered by pushing a tag that looks like a valid semver
and it should start with `v`. For example adding a tag like `v0.1.1` would trigger a release from the CI/CD. The tag
should match the tag in pyproject.toml with the `v` omitted in the `.toml` file. The deployment step will fail if the
version in the `.toml` file does not match the version in the tag.

Due to [some known issues](https://gitlab.com/gitlab-org/gitlab-foss/-/issues/27818) we can't inspect the tag **and**
the branch but by convention releases should only happen on the `master` branch. Note that all tags that start with a
`v` are protected and only project maintainers can create them.
