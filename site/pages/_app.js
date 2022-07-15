import "../styles/globals.css";
import { EuiProvider } from "@elastic/eui";

function MyApp({ Component, pageProps }) {
  return (
    <EuiProvider colorMode="light">
      <Component {...pageProps} />
    </EuiProvider>
  );
}

export default MyApp;
