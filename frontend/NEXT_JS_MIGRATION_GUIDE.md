# Moving VIBE E-Commerce to Next.js

This guide outlines the steps to migrate the existing React (CRA) frontend to Next.js 14+ (App Router) to enable Server-Side Rendering (SSR) and improve SEO/Performance.

## 1. Prerequisites
- Node.js 18+
- Existing backend running on port 8000 (Django)

## 2. Installation
Install Next.js and remove `react-scripts`.

```bash
npm install next react react-dom
npm uninstall react-scripts
```

## 3. Project Restructuring

### App Router Structure
Create a new `app` directory at `frontend/src/app` (or `frontend/app` if moving out of src).

```
frontend/
  app/
    layout.js      # Wraps all pages (replace App.js logic here)
    page.js        # Homepage (move AgriHome logic here)
    products/
      page.js      # /products list
      [slug]/
        page.js    # /products/:slug details
    loading.js     # Suspense fallback
    error.js       # Error boundary
```

### Migrating `App.js`
The logic in `App.js` (Providers, Header, Footer) moves to `app/layout.js`.

```javascript
// app/layout.js
import ThemeContextProvider from '../utils/ThemeContext';
// ... imports

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ThemeContextProvider>
          <AuthProvider>
            <CartProvider>
              <Header />
              <main>{children}</main>
              <Footer />
            </CartProvider>
          </AuthProvider>
        </ThemeContextProvider>
      </body>
    </html>
  );
}
```

## 4. Routing Changes
Replace `react-router-dom`:
- Remove `<BrowserRouter>`, `<Routes>`, `<Route>`.
- Replace `useNavigate` with `useRouter` from `next/navigation`.
- Replace `<Link to="...">` with `<Link href="...">` from `next/link`.
- Replace `useParams` with page props `params` (in Server Components) or `useParams` (in Client Components).

## 5. Data Fetching (SSR)
In Next.js, fetch data directly in Server Components (`page.js`).

```javascript
// app/products/[slug]/page.js
async function getProduct(slug) {
  const res = await fetch(`http://localhost:8000/api/products/${slug}/`, { cache: 'no-store' });
  return res.json();
}

export default async function ProductPage({ params }) {
  const product = await getProduct(params.slug);
  return <ProductDetailEnhanced product={product} />;
}
```

## 6. Styling
- Keep `App.css` and `index.css`. Import them in `app/layout.js`.
- Material UI (MUI) requires a client-side registry for SSR. Follow [MUI Next.js Guide](https://mui.com/material-ui/guides/next-js-app-router/).

## 7. Optimization
- **Images**: Replace `<img>` (or `LazyImage`) with `next/image`.
- **Fonts**: Use `next/font`.
- **SEO**: Export `metadata` object from pages.

```javascript
export const metadata = {
  title: 'VIBE E-Commerce',
  description: 'Premium Agri-Store',
};
```

## 8. Deployment
Update `package.json`:
```json
"scripts": {
  "dev": "next dev",
  "build": "next build",
  "start": "next start"
}
```

## Checkpoints
- [ ] Dependencies updated
- [ ] `app/layout.js` created
- [ ] `react-router-dom` usage replaced
- [ ] API calls moved to Server Components where possible
- [ ] MUI Registry implemented
