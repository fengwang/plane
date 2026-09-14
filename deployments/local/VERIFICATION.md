# Local deployment verification

Validated on Linux x86-64, 2026-09-14. Test records were created only in the workstation's local deployment.

| Check                        | Evidence                                                                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Production builds            | Web, admin, space, live and backend Dockerfiles built locally                                                                                         |
| Fresh startup                | Empty database migrated; RustFS directories initialized automatically; uploads bucket created                                                         |
| Configuration                | Seven rendered-Compose contract tests cover source builds, one published port, persistence, startup dependencies, SMTP defaults and internal Live URL |
| Frontend bursts              | HTTP regression test sends 350 requests each to web and admin; passed after replacing local static rate limiter configuration                         |
| Initial setup                | Instance administrator created through `/god-mode/`, with SMTP empty                                                                                  |
| Login and creation           | Browser password login, ordinary user signup without SMTP, workspace creation, project creation and work-item creation succeeded                      |
| Plain HTTP on a LAN address  | Saved work item loaded through the workstation LAN IP; a page edit survived reload with the browser reporting an insecure context                     |
| S3 uploads                   | Browser POST to `/uploads` returned 204; attachment completion returned 204                                                                           |
| S3 downloads                 | Browser download matched uploaded PNG byte-for-byte (SHA-256 `c7357bda527de8ea320ffa03d4db58668c9ad52ab038efc4d840a59df7dcae02`)                      |
| Collaboration                | An edit in a second tab appeared in the first without reload; merged content stored in PostgreSQL                                                     |
| Internal document conversion | API-to-Live request returned 200 with editor JSON and binary data                                                                                     |
| Public views                 | Anonymous browser displayed the published work item; SSR title matched the project name                                                               |
| Runtime URL helper           | Four Node unit tests cover internal runtime address, development configuration, same-origin fallback and a captured build-time API origin             |
| Type and lint checks         | Space and its dependencies passed the targeted TypeScript check; changed application files passed OxLint                                              |

Container recreation also passed: after Compose down and up with freshly rebuilt images, the work item, merged page HTML and Valkey marker survived. A new browser download retained the same SHA-256.

## LAN server deployment

The server at `10.147.19.203` pulled implementation commit `8306a76d3` from the fork's `local` branch and built all application images from source in `/data/Dockers/plane`. Its existing upstream remote and unrelated Compose file were preserved; a separate `fork` remote tracks this deployment branch.

Fresh migrations and RustFS initialization exited successfully. All long-running services started, all configured health checks passed, and only host port `17239` was published. The uploads bucket returned 200 to an authenticated S3 HEAD request. From the workstation, `/healthz`, `/api/instances/`, `/live/health` and `/spaces/` returned 200, and the eight deployment tests passed, including 700 requests to the server's web/admin routes.

A browser opened `http://10.147.19.203:17239`, followed Get started, and displayed the administrator registration form at `/god-mode/`. This form was left unsubmitted so the owner can create the first administrator. The server uses its own root `.env`, generated secrets and persistent `data/` directories; workstation test accounts were not copied to it.

## Existing application behavior observed

The application emits a recoverable React hydration warning on initial navigation; the tested flows remained usable. Its existing signature-based file detection rejects plain text attachments with an empty detected MIME type (`packages/services/src/file/helper.ts`). The attachment round-trip above uses a PNG that the application recognizes. These behaviors are separate from storage and network configuration.

Email delivery and SMTP-dependent password resets were not tested because SMTP is intentionally unconfigured. The public view is accessible without login; the main app and instance administration retain their normal authentication.
