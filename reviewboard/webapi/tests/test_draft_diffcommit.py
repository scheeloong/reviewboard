from djblets.features.testing import override_feature_checks
        with override_feature_checks(self.override_features):
            rsp = self.api_post(
                get_draft_diffcommit_list_url(review_request,
                                              diffset.revision),
                dict(self._DEFAULT_POST_DATA, **{
                    'diff': SimpleUploadedFile('diff', b'     ',
                                               content_type='text/x-patch'),
                }),
                expected_status=400)
            with override_feature_checks(self.override_features):
                rsp = self.api_post(
                    get_draft_diffcommit_list_url(review_request,
                                                  diffset.revision),
                    dict(self._DEFAULT_POST_DATA, **{
                        'diff': diff,
                    }),
                    expected_status=400)
        with override_feature_checks(self.override_features):
            rsp = self.api_post(
                get_draft_diffcommit_list_url(review_request,
                                              diffset.revision),
                dict(self._DEFAULT_POST_DATA, **{
                    'diff': diff,
                }),
                expected_status=400)
        with override_feature_checks(self.override_features):
            rsp = self.api_post(
                get_draft_diffcommit_list_url(review_request,
                                              diffset.revision),
                dict(self._DEFAULT_POST_DATA, **{
                    'diff': diff,
                    'parent_diff': parent_diff,
                }),
                expected_mimetype=draft_diffcommit_item_mimetype)
        with override_feature_checks(self.override_features):
            rsp = self.api_post(
                get_draft_diffcommit_list_url(review_request,
                                              diffset.revision),
                dict(self._DEFAULT_POST_DATA, **{
                    'commit_id': 'r0',
                    'parent_id': 'r1',
                    'diff': diff,
                    'parent_diff': parent_diff,
                }),
                expected_mimetype=draft_diffcommit_item_mimetype,
                expected_status=201)

        with override_feature_checks(self.override_features):
            rsp = self.api_post(
                get_draft_diffcommit_list_url(review_request,
                                              diffset.revision),
                dict(self._DEFAULT_POST_DATA, **{
                    'commit_id': 'r0',
                    'parent_id': 'r1',
                    'diff': diff,
                    'committer_date': 'Jun 1 1990',
                    'author_date': 'Jun 1 1990',
                }),
                expected_status=400)
    @webapi_test_template
    def test_post_subsequent(self):
        """Testing the POST <URL> API with a subsequent commit"""
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(
            repository=repository,
            submitter=self.user,
            create_with_history=True)
        diffset = self.create_diffset(review_request, draft=True)

        commit = self.create_diffcommit(
            repository,
            diffset,
            diff_contents=self._DEFAULT_DIFF_CONTENTS)

        validation_info = \
            resources.validate_diffcommit.serialize_validation_info({
                commit.commit_id: {
                    'parent_id': commit.parent_id,
                    'tree': {
                        'added': [],
                        'modified': [{
                            'filename': 'readme',
                            'revision': '5b50866',
                        }],
                        'removed': [],
                    },
                },
            })

        diff = SimpleUploadedFile(
            'diff',
            (b'diff --git a/readme b/readme\n'
             b'index 5b50866..f00f00f 100644\n'
             b'--- a/readme\n'
             b'+++ a/readme\n'
             b'@@ -1 +1,4 @@\n'
             b' Hello there\n'
             b' \n'
             b' Oh hi!\n'
             b'+Goodbye!\n'),
            content_type='text/x-patch')

        with override_feature_checks(self.override_features):
            rsp = self.api_post(
                get_draft_diffcommit_list_url(review_request,
                                              diffset.revision),
                dict(self._DEFAULT_POST_DATA, **{
                    'commit_id': 'r2',
                    'parent_id': 'r1',
                    'diff': diff,
                    'validation_info': validation_info,
                }),
                expected_mimetype=draft_diffcommit_item_mimetype)

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('draft_commit', rsp)

        item_rsp = rsp['draft_commit']
        self.compare_item(item_rsp, DiffCommit.objects.get(pk=item_rsp['id']))
