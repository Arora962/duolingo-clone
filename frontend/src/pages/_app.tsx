import "~/styles/globals.css";
import type { AppProps } from "next/app";
import { ToastViewport } from "~/components/ui/Toast";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Component {...pageProps} />
      <ToastViewport />
    </>
  );
}
