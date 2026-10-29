import { useEffect } from "react";
import {
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import Analyze from "./pages/Analyze";
import Landing from "./pages/Landing";

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return null;
}

const NAV_LINK_CLASS = ({ isActive }: { isActive: boolean }) =>
  `rounded-lg px-3 py-2 text-sm font-medium transition ${
    isActive
      ? "bg-indigo-50 text-indigo-700"
      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
  }`;

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-800">
      <ScrollToTop />
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-6 py-3">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-base font-bold text-white">
              G
            </span>
            <span className="leading-tight">
              <span className="block font-bold text-slate-900">GAPMATE</span>
              <span className="hidden text-xs text-slate-500 sm:block">
                Định hướng nghề nghiệp cho người trẻ
              </span>
            </span>
          </Link>

          <nav className="ml-auto flex items-center gap-1">
            <NavLink to="/" end className={NAV_LINK_CLASS}>
              Trang chủ
            </NavLink>
            <NavLink to="/analyze" className={NAV_LINK_CLASS}>
              Phân tích CV
            </NavLink>
            <Link
              to="/analyze"
              className="ml-2 hidden rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500 sm:block"
            >
              Chấm CV miễn phí
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-6 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <p>
            <span className="font-semibold text-slate-700">GAPMATE</span> — Biết
            mình thiếu gì trước khi nhà tuyển dụng nói ra.
          </p>
          <a
            href="https://github.com/kappyphm/gapmate-demo"
            target="_blank"
            rel="noreferrer"
            className="shrink-0 transition hover:text-indigo-600"
          >
            GitHub ↗
          </a>
        </div>
      </footer>
    </div>
  );
}
