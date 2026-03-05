## creating new project

instead of `pip install -r requirements.txt`, do `make install`

## posting new version

3. make changes
4. manually update CHANGELOG.md to just the most recent changes
5. manually update version.py
6. do a commit + push

## for new release

```bash
# this line is only needed if you haven't done a commit yet
git commit -am "Prepare release 1.2.0"

# these lines do the release
git tag -a v1.2.0 -m "Release v1.2.0"
git push
git push origin v1.2.0
```
