# PHM Consulting website

The website text lives in `content/*.json`. Kris and Yasmin edit it at **/admin**. Every time something changes, Netlify runs `python3 _src/build.py` and publishes the finished pages from `public/`.

```
content/          all website text, one file per page (edited through /admin)
assets/           logo and photos; photos uploaded in /admin go to assets/uploads/
admin/            the editing panel (Decap CMS): index.html + config.yml
_src/             build script, styles and scripts (developer only)
netlify/functions/client-intake.mjs   enquiry form -> email to phmconsulting.advisory@gmail.com
netlify.toml, package.json            Netlify settings
```

What the client can change: page text, headings, button labels, services (add, remove, reorder), bios, titles, photos, FAQs, testimonials, footer text, email and Instagram links, and the text Google shows.
What stays fixed: layout, colours, fonts, page structure and the enquiry form fields.

## One-time setup of the login (developer)

1. **GitHub OAuth app.** GitHub → your profile photo → Settings → Developer settings → OAuth Apps → New OAuth App.
   - Application name: `PHM Website Editor`
   - Homepage URL: `https://phm-consulting.netlify.app` (change to `https://www.phmconsulting.ca` after launch)
   - Authorization callback URL: `https://api.netlify.com/auth/done`
   - Register, then copy the **Client ID** and click **Generate a new client secret** and copy it.
2. **Netlify.** Project `phm-consulting` → Project configuration → Access & security → OAuth → Authentication providers → Install provider → **GitHub** → paste the Client ID and Client secret → Install.
3. **Test.** Open `https://phm-consulting.netlify.app/admin` → Login with GitHub.
4. **Add the editors.** Kris and Yasmin each create a free account at github.com. Then in this repository: Settings → Collaborators → Add people → their GitHub username or email. They accept the email invitation once.

`admin/config.yml` points at the repository `AkxshHans/phm-website`. If the repository is moved or renamed (for example into PHM's own GitHub account), update the `repo:` line.

## Enquiry email

See the Netlify environment variables: `RESEND_API_KEY`, `FROM_EMAIL`, `SITE_ORIGIN`. The recipient is fixed in `netlify/functions/client-intake.mjs`.

---

# How to edit the website (for Kris and Yasmin)

1. Go to **phmconsulting.ca/admin** and click **Login with GitHub**.
2. Click **Website pages**, then the page you want: Home, About Us, Services, Canadian Market Entry, Contact, Testimonials, or Footer and contact details.
3. Change the text in the boxes. In lists (services, FAQs, testimonials, team), use **Add** to add an item, drag the handle to reorder, and the **×** to remove one.
4. To change a photo, click **Choose different image** and upload. Portraits work best at least 1000 pixels wide.
5. Click **Publish → Publish now** at the top. The live website updates in about one minute. Refresh the page to see it.

Tips
- Keep headlines short, especially on phones.
- Testimonials: name, role and organization are optional. Untick "Show the scrolling testimonials" to hide them all.
- Only one service should have "Button opens the Canadian Market Entry page" ticked.
- If something looks wrong after publishing, open the same page in /admin, fix it and publish again. Every change is saved in history, so your developer can restore any earlier version.
