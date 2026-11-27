# PHM Consulting website: setup and launch notes

Static site (4 pages) plus one serverless function and a small content admin. Built to the *PHM Consulting Developer Instructions* (latest revision). Hosting assumed: **Netlify** (free tier is enough to start). Confirm any paid plan with PHM before enabling it.

```
index.html, about.html, services.html, contact.html   pages (client-intake.html forwards to contact.html)
services/canadian-market-entry/index.html   Canadian Market Entry and Business Setup page (live URL: /services/canadian-market-entry)
assets/instagram-qr.png     QR code for https://www.instagram.com/phmconsulting/ (verified to scan)
assets/                     logo, headshots, photos
data/quotes.json            client quotes (home carousel, About, Services), edited through /admin
admin/                      Decap CMS (login-protected editing area)
netlify/functions/client-intake.mjs   POST /api/client-intake → email to PHM
netlify.toml, package.json  hosting config
sitemap.xml, robots.txt     search setup
```

## 1. Deploy

1. Put this folder in a Git repository **owned by PHM** (GitHub account in PHM's name).
2. In Netlify: *Add new site → Import from Git*, select the repo. Build command: none. Publish directory: `.`
3. Connect the domain `www.phmconsulting.ca` (Domain management) and turn on HTTPS.

## 2. Enquiry email (guide section 7)

The "Let's Talk" form posts JSON to `/api/client-intake`. The function validates every field on the server (name and email required, email format, one of the 6 "How can we help?" choices, budget amount OR one alternative, never both), rejects the spam honeypot and anything submitted in under 3 seconds, limits bodies to 16 KB, checks the origin, rate-limits to 5 requests a minute per visitor, removes duplicate retries for 24 hours, and returns `{"ok":true}` **only after the email provider accepts the message**. The recipient is fixed in code: `phmconsulting.advisory@gmail.com`.

1. Create a **Resend** account (resend.com) in PHM's name and verify the domain `phmconsulting.ca` (adds DNS records).
2. In Netlify → *Site configuration → Environment variables*, add:
   - `RESEND_API_KEY`: API key from Resend
   - `FROM_EMAIL`: `PHM Consulting Website <enquiries@phmconsulting.ca>`
   - `SITE_ORIGIN`: `https://www.phmconsulting.ca` (add the Netlify preview URL too, comma-separated, while testing)
3. Redeploy. Email subject: `New PHM enquiry — [service] — [organization]`; Reply-To is the client's email; the body lists every answer with its label and the receipt time.

## 3. Client quotes admin (instructions section 4)

`/admin` opens Decap CMS. Each quote has: Shown on (home, about, services), Display order, Status (draft/published), Sample (shows the staging label), Quote, Name, Role, Organization. The homepage shows a manual carousel, one quote at a time, with previous/next buttons and no auto-rotation. About and Services show one quote each. There are no quotes on Contact.

**Quotes are currently switched off (status: draft)**, as the revision guide says not to publish invented testimonials. When PHM has approved, permissioned quotes: add them in /admin, set Status to published and untick Sample. They appear as a small carousel on Home and one short quote each on About and Services. Nothing shows while all quotes are drafts.

1. Netlify → *Identity* → enable, registration **Invite only**, enable **Git Gateway**.
2. Invite Kris and Yasmin by email.
3. If Netlify Identity isn't available, change `backend` in `admin/config.yml` to `name: github` with `repo: <owner>/<repo>`.

## 4. Still to complete before launch

| Guide item | What's needed |
|---|---|
| D2 Accounts | Domain, Netlify, Resend, GitHub and Google accounts owned by PHM; record owner, login URL, renewal date, cost and billing contact for each |
| D4 Analytics | Choose a service (e.g. Plausible or GA4). Add the GA4 tag to every page's `<head>`. The site already sends `consultation_request` (consultation buttons) and `generate_lead` (successful enquiry) through `gtag`/`dataLayer`, with no personal form answers |
| D5 Search | Google Search Console for https://phmconsulting.ca, submit `sitemap.xml`. Canonicals point to phmconsulting.ca; any other host (GitHub/staging preview) automatically gets `noindex`. Structured data (ProfessionalService) on the homepage uses only name, website, email, logo, tagline and "Canada" as the service area. Check Google Business Profile eligibility; add no address unless accurate |
| Privacy | The form shows a one-line privacy notice ("We use the details you share only to respond to your enquiry.") — PHM to approve. Add a full privacy page once PHM approves wording (services receiving data: Netlify hosting and functions, Resend email, chosen analytics). Link it from the footer and form only after approval |
| D3 Backups | Git history backs up content and code; enable Netlify deploy history; decide how long enquiry emails are kept |
| D1/D11 | Recorded walkthrough of the admin; one-page account and maintenance guide |
| Photos | Demo photos came from Pinterest. Replace with PHM's own or licensed images before launch |

## 5. Launch checks (instructions section 8)

- [ ] All wording matches the instructions; staging quotes replaced or set to draft
- [ ] The five service names are identical on Services, Contact, navigation and links
- [ ] Form: required fields, email format, budget amount vs alternatives, spam protection, privacy notice
- [ ] Fictional test enquiry arrives at phmconsulting.advisory@gmail.com (check Spam); success message shows; failure keeps answers
- [ ] Footer links, buttons, headings and logo correct on mobile and desktop
- [ ] Canonical URLs, sitemap, robots.txt, indexing and GA4 events verified on the live domain
- [ ] Staging link approved by Kris and Yasmin before publishing to phmconsulting.ca

## 6. Revision guide notes (latest)

- Service 05 is now "Canadian Market Entry and Business Setup" everywhere (Home, Services, Contact form, email function).
- Its button opens /services/canadian-market-entry; that page's "Discuss Your Business Plans" button opens the contact form with service 05 pre-selected.
- The FAQ answers on the Canadian Market Entry page are DRAFTS for PHM approval before going live.
- Header offsets: the page sets --hdr from the real header height, so anchor jumps and scrolling never hide headings under the fixed header.
- Smooth scrolling and most animation are off on phones and for visitors who prefer reduced motion. No text depends on scrolling to become readable.
