## creating new project

instead of `pip install -r requirements.txt`, do `make install`

## posting new version

3. make changes
4. manually update CHANGELOG.md to just the most recent changes
5. ~~manually update version.py~~
6. do a commit + push

## for new release

```bash
# this line is only needed if you haven't done a commit yet
git commit -am "Prepare release 1.2.0"

# create and push the tag
git tag -a v2026.11.14.1 -m "Release v2026.11.14.1"
git push
git push origin v2026.11.14.1

# create the GitHub Release (pick one option)

# Option 1: simple one-line notes
gh release create v2026.11.14.1 --title "v2026.11.14.1" --notes "Brief description here"

# Option 2: multi-line notes inline
gh release create v2026.11.14.1 --title "v2026.11.14.1" --notes "$(cat <<'EOF'
## What's New

- Feature A
- Feature B

## Bug Fixes

- Fixed issue X
EOF
)"

# Option 3: notes from a markdown file (e.g., CHANGELOG.md or a dedicated release-notes.md)
gh release create v2026.11.14.1 --title "EPICpy Fall Cleanup" --notes-file RELEASE-NOTES.md
```

---

### If you need to setup gh cli app

```bash
sudo apt install gh-cli
```

```
$ gh auth login
? What account do you want to log into? GitHub.com
? What is your preferred protocol for Git operations on this host? HTTPS <---- Choose This One
? Authenticate Git with your GitHub credentials? Yes
? How would you like to authenticate GitHub CLI?
> Login with a web browser  <---- Choose This One
```