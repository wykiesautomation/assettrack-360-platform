# AssetTrack 360 Public SEO Deployment and Submission

## Deploy
1. Deploy this cumulative repository build without changing the current domain or DNS.
2. Confirm the public homepage and every public product URL returns HTTP 200 without login.
3. Confirm `/robots.txt`, `/sitemap.xml`, `/BingSiteAuth.xml`, and the Google verification file return HTTP 200.
4. Confirm private customer, admin, API, device-studio and billing routes are not in the sitemap.

## Priority public URLs
- https://assettrack360.wykiesautomation.co.za/
- https://assettrack360.wykiesautomation.co.za/fleet-tracking
- https://assettrack360.wykiesautomation.co.za/industrial-asset-monitoring
- https://assettrack360.wykiesautomation.co.za/tank-level-monitoring
- https://assettrack360.wykiesautomation.co.za/device-engineering-studio
- https://assettrack360.wykiesautomation.co.za/diesel-security
- https://assettrack360.wykiesautomation.co.za/opc-ua-monitoring
- https://assettrack360.wykiesautomation.co.za/modbus-monitoring
- https://assettrack360.wykiesautomation.co.za/about
- https://assettrack360.wykiesautomation.co.za/contact

## Bing Webmaster Tools
1. Verify `assettrack360.wykiesautomation.co.za`.
2. Submit `https://assettrack360.wykiesautomation.co.za/sitemap.xml`.
3. Submit the homepage and the first four priority product pages under URL Submission.
4. Configure IndexNow only after generating and protecting the domain-specific IndexNow key.

## Google Search Console
1. Verify the domain or URL-prefix property.
2. Submit `https://assettrack360.wykiesautomation.co.za/sitemap.xml`.
3. Use URL Inspection on the homepage and priority pages.
4. Request indexing after the deployed pages return HTTP 200 and the canonical URL matches the inspected URL.

## Release checks
- Only one canonical hostname: `https://assettrack360.wykiesautomation.co.za`.
- No demo or private data appears on public pages.
- Customer Login remains separate from public product navigation.
- Search titles and descriptions are unique.
- Open Graph and structured data remain present.
