# Auto-updating Instagram stats: your part

The site already reads its follower, post and average-view numbers from `data/stats.json`.
A GitHub Action (`.github/workflows/update-stats.yml`) refreshes that file **every day at 6:00 AM IST**
using Instagram's official API. Until it runs for the first time, the site shows the numbers written
in `index.html`.

You need to do 4 things once. They involve your own accounts and logins, so only you can do them.
Total time: about 20–30 minutes.

---

## 1. Put the site on GitHub Pages (free hosting)

1. Sign in at <https://github.com> (create a free account if you don't have one).
2. Click **New repository**. Name it something like `peeyush-portfolio`, set it to **Public**, and create it.
3. Upload everything in this `portfolio_chronicles` folder **except** the `reels` and `.claude` folders
   (the `.gitignore` file already skips those if you use Git or GitHub Desktop).
   - Easiest: on the repo page click **Add file → Upload files** and drag the files and folders in.
   - Make sure `.github/workflows/update-stats.yml` is included. Hidden folders starting with a dot are
     easy to miss when dragging; GitHub Desktop handles them automatically.
4. In the repo, go to **Settings → Pages**. Under **Build and deployment**, choose
   **Deploy from a branch**, branch **main**, folder **/ (root)**, and save.
5. After a minute your site is live at `https://<your-github-username>.github.io/peeyush-portfolio/`.
   That's the link for your Instagram bio.

## 2. Create a Meta developer app (gives you the Instagram API token)

Your Instagram account must be a **Creator** or **Business** account (Instagram app →
Settings → Account type and tools). If you can see Insights on your reels, it already is.

1. Go to <https://developers.facebook.com>, log in, and click **My Apps → Create app**.
2. Pick the use case **"Manage messaging & content on Instagram"** (this is
   *Instagram API with Instagram Login*, so no Facebook Page is needed). Give the app any name.
3. In the app dashboard open **Instagram → API setup with Instagram login**.
4. Under **Generate access tokens**, click **Add account**, log in with `@peeyush.chronicles`,
   and approve the permissions (`instagram_business_basic` and
   `instagram_business_manage_insights`).
5. Click **Generate token** next to your account and copy it. This is a long-lived token
   (valid 60 days). **Treat it like a password:** don't post it anywhere or paste it in chat.

You can leave the app in Development mode; it only needs to read your own account.

## 3. Add the token to GitHub as a secret

1. In your repo: **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: `IG_ACCESS_TOKEN`. Value: the token you copied. Save.

### Optional, but recommended: make the token never expire

The workflow refreshes the token every day. To let it save the refreshed token back
automatically, add a second secret:

1. Go to <https://github.com/settings/personal-access-tokens/new> (fine-grained token).
2. **Repository access:** only `peeyush-portfolio`. **Permissions → Repository permissions →
   Secrets:** Read and write. Set the expiry as long as you like (up to 1 year), then generate and copy it.
3. Add it as a repository secret named `GH_PAT`.

Without `GH_PAT`, generate a fresh Instagram token (step 2.5) every ~50 days and replace
the `IG_ACCESS_TOKEN` secret.

## 4. Run it once to test

1. In the repo, open the **Actions** tab. If asked, click **I understand… enable workflows**.
2. Click **Update Instagram stats → Run workflow**.
3. When it turns green, a `data/stats.json` file appears in the repo, and your live site
   shows a small line under the stats: *"Live from Instagram · updated …"*.

If it fails, open the failed run and copy the error text (it never prints your token).
Then ask Claude to look at it.

---

### What gets calculated
- **Followers** and **posts**: straight from your profile.
- **Average views per reel**: average across your 12 most recent reels, skipping any reel
  posted in the last 2 days (those are still gaining views). Shown as e.g. "20K+".
