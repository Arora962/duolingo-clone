import { useEffect } from "react";
import type { AppProps } from "next/app";
import "~/styles/globals.css";
import { ToastViewport } from "~/components/ui/Toast";
import { useDarkMode } from "~/hooks/useDarkMode";
import { useLearner } from "~/store/useLearner";
import { useSettings } from "~/store/useSettings";

function AppBootstrap() {
  const refreshMe = useLearner((state) => state.refresh);
  const refreshSettings = useSettings((state) => state.refresh);

  useDarkMode();

  useEffect(() => {
    void refreshMe();
    void refreshSettings();
  }, [refreshMe, refreshSettings]);

  return null;
}

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <AppBootstrap />
      <Component {...pageProps} />
      <ToastViewport />
    </>
  );
}
