"""
Accessor class to produce dictionary representations of bundles, cached as json.
"""

class DocCache(object):

    templates = {
        'bundle' : 'bundles/{vid}/bundle.json',
        'schema' : 'bundles/{vid}/schema.json',
        'table' : 'bundles/{bvid}/tables/{tvid}.json',
        'library' : 'library.json',
        'manifest': 'manifests/{uid}.json',
        'stores': 'stores/{uid}.json',

    }

    def __init__(self, cache):

        self.cache = cache

    def path(self, t, **kwargs):

        return  self.cache.path(t.format(**kwargs), missing_ok = True)

    def munge(self,n):
        import sys
        import re

        if sys.platform == 'darwin':
            # Mac OS has case-insensitive file systems which cause aliasing in vids,
            # so we add a '_' before the uppercase letters.

            return re.sub(r'([A-Z])', lambda p: '_' + p.group(1), n)
        else:

            return n

    def resolve_vid(self, vid):

        return self.munge(vid)

    def has(self, rel_path):

        return self.cache.has(rel_path)

    def put(self, rel_path, f, force=False):
        import json

        if self.cache.has(rel_path) and not force:
            return False

        with self.cache.put_stream(rel_path) as s:
            json.dump(f(), s, indent=2)

        return True

    def get(self, rel_path):
        import json

        if not self.cache.has(rel_path):

            return None

        with self.cache.get_stream(rel_path) as s:
            return json.load(s)

    ##
    ## Library

    def library_path(self):
        return self.path(self.templates['library'])

    def put_library(self, l, force=False):
        return self.put(self.library_path(), lambda:l.dict, force=force)

    def get_library(self):

        return self.get(self.library_path())

    ##
    ## Manifests

    def manifest_path(self, uid):
        return self.path(self.templates['manifest'], uid=self.resolve_vid(uid))

    def put_manifest(self, m,f, force=False):

        d = m.dict
        d['file'] = f.dict
        d['text'] = str(m)

        return self.put(self.manifest_path(m.uid), lambda: d, force=force)

    def get_manifest(self, vid):
        return self.get(self.manifest_path(vid))

    ##
    ## Stores

    def store_path(self, vid):
        return self.path(self.templates['store'], vid=self.resolve_vid(vid))

    def put_store(self, b, force=False):
        return self.put(self.store_path(b.identity.vid), lambda: b.dict, force=force)

    def get_store(self, vid):
        return self.get(self.store_path(vid))

    ##
    ## Bundles

    def bundle_path(self, vid):
        return self.path(self.templates['bundle'], vid=self.resolve_vid(vid))

    def put_bundle(self, b, force=False):
        return self.put(self.bundle_path(b.identity.vid), lambda: b.dict)

    def get_bundle(self, vid):
        return self.get(self.bundle_path(vid))

    ##
    ## Schemas

    def schema_path(self, vid):
        return self.path(self.templates['schema'], vid=self.resolve_vid(vid))

    def put_schema(self, b, force=False):
        return self.put(self.schema_path(b.identity.vid), lambda: b.schema.dict)

    def get_schema(self, vid):
        return self.get(self.schema_path(vid))

    ##
    ## Tables

    def table_path(self, bvid, tvid):
        return self.path(self.templates['table'], bvid=self.resolve_vid(bvid), tvid=self.resolve_vid(tvid))

    def put_table(self, t, force=False):
        bvid = t.d_vid

        return self.put(self.table_path(bvid, t.vid), lambda: t.nonull_col_dict )

    def get_table(self, tvid):
        bvid = 'd'+tvid[1:-5]+tvid[-3:]
        return self.get(self.table_path(bvid,tvid))
