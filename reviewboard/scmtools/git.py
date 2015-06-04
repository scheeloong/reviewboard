from django.utils.six.moves.urllib.parse import (quote as urlquote,
                                                 urlsplit as urlsplit,
                                                 urlunsplit as urlunsplit)
    def get_file(self, path, revision=HEAD, **kwargs):
    def file_exists(self, path, revision=HEAD, **kwargs):
    EXTENDED_HEADERS_KEYS = set([
        b'old mode',
        b'new mode',
        b'deleted file mode',
        b'new file mode',
        b'copy from',
        b'copy to',
        b'rename from',
        b'rename to',
        b'similarity index',
        b'dissimilarity index',
        b'index',
    ])

    def _parse_extended_headers(self, linenum):
        """Parse an extended headers section.

        A dictionary with keys being the header name and values
        being a tuple of (header value, complete header line) will
        be returned. The complete header lines will have a trailing
        new line added for convenience.
        """
        headers = {}

        while linenum < len(self.lines):
            line = self.lines[linenum]

            for key in self.EXTENDED_HEADERS_KEYS:
                if line.startswith(key):
                    headers[key] = line[len(key) + 1:], line + b'\n'
                    break
            else:
                # No headers were found on this line so we're
                # done parsing them.
                break

            linenum += 1

        return headers, linenum

            line, info = self._parse_git_diff(linenum)
            return line, info, True
        # Assume the blob / commit information is provided globally. If
        # we found an index header we'll override this.
        file_info.origInfo = self.base_commit_id
        file_info.newInfo = self.new_commit_id
        headers, linenum = self._parse_extended_headers(linenum)

        if self._is_new_file(headers):
            file_info.data += headers[b'new file mode'][1]
            file_info.origInfo = PRE_CREATION
        elif self._is_deleted_file(headers):
            file_info.data += headers[b'deleted file mode'][1]
        elif self._is_mode_change(headers):
            file_info.data += headers[b'old mode'][1]
            file_info.data += headers[b'new mode'][1]

        if self._is_moved_file(headers):
            file_info.origFile = headers[b'rename from'][0]
            file_info.newFile = headers[b'rename to'][0]
            if b'similarity index' in headers:
                file_info.data += headers[b'similarity index'][1]
            file_info.data += headers[b'rename from'][1]
            file_info.data += headers[b'rename to'][1]
        elif self._is_copied_file(headers):
            file_info.origFile = headers[b'copy from'][0]
            file_info.newFile = headers[b'copy to'][0]
            if b'similarity index' in headers:
                file_info.data += headers[b'similarity index'][1]

            file_info.data += headers[b'copy from'][1]
            file_info.data += headers[b'copy to'][1]

        if b'index' in headers:
            index_range = headers[b'index'][0].split()[0]
            file_info.data += headers[b'index'][1]
    def _is_new_file(self, headers):
        return b'new file mode' in headers
    def _is_deleted_file(self, headers):
        return b'deleted file mode' in headers
    def _is_mode_change(self, headers):
        return b'old mode' in headers and b'new mode' in headers
    def _is_copied_file(self, headers):
        return b'copy from' in headers and b'copy to' in headers
    def _is_moved_file(self, headers):
        return b'rename from' in headers and b'rename to' in headers
        url_parts = urlsplit(self.path)

        if (url_parts.scheme.lower() in ('http', 'https') and
            url_parts.username is None and self.username):
            # Git URLs, especially HTTP(s), that require authentication should
            # be entered without the authentication info in the URL (because
            # then it would be visible), but we need it in the URL when testing
            # to make sure it exists. Reformat the path here to include them.
            new_netloc = urlquote(self.username, safe='')

            if self.password:
                new_netloc += ':' + urlquote(self.password, safe='')

            new_netloc += '@' + url_parts.netloc

            path = urlunsplit((url_parts[0], new_netloc, url_parts[2],
                               url_parts[3], url_parts[4]))
        else:
            path = self.path

        p = self._run_git(['ls-remote', path, 'HEAD'])