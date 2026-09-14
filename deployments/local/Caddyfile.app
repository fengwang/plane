# Local production frontend serving. One navigation can request hundreds of
# chunks, so do not apply the upstream 300-requests/minute static asset limit.
:3000 {
	root * /usr/share/caddy/html
	header {
		X-Frame-Options "DENY"
		X-Content-Type-Options "nosniff"
	}
	try_files {path} {$SPA_INDEX:/index.html}
	file_server
}
