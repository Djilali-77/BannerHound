import { useCallback, useEffect, useRef, useState } from "react";
import { API_URL } from "../lib/api";

/**
 * Runs a live scan using Server-Sent Events (SSE).
 *
 * status: "idle" | "scanning" | "done" | "stopped" | "error"
 *
 * Events sent by the API:
 *   start       { scan_id }          scan accepted
 *   hosts       { total }            number of live hosts found
 *   (default)   one result row per host
 *   scan_error  { message }          something went wrong
 *   close       { scan_id, total }   scan finished
 */
export function useScan() {
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [total, setTotal] = useState(null);
  const [scanId, setScanId] = useState(null);
  const sourceRef = useRef(null);

  const closeStream = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
  }, []);

  const start = useCallback(
    (subnet) => {
      closeStream();
      setResults([]);
      setError("");
      setTotal(null);
      setScanId(null);
      setStatus("scanning");

      const url = `${API_URL}/api/scan/stream?subnet=${encodeURIComponent(subnet.trim())}`;
      const source = new EventSource(url);
      sourceRef.current = source;

      // The API sends a "close" event after "scan_error", so remember the failure
      let failed = false;

      source.addEventListener("start", (event) => {
        setScanId(JSON.parse(event.data).scan_id);
      });

      source.addEventListener("hosts", (event) => {
        setTotal(JSON.parse(event.data).total);
      });

      source.onmessage = (event) => {
        const device = JSON.parse(event.data);
        setResults((previous) => [...previous, device]);
      };

      source.addEventListener("scan_error", (event) => {
        failed = true;
        setError(JSON.parse(event.data).message);
        setStatus("error");
      });

      source.addEventListener("close", (event) => {
        const data = JSON.parse(event.data);
        if (data.scan_id) setScanId(data.scan_id);
        if (!failed) setStatus("done");
        source.close();
        sourceRef.current = null;
      });

      // Fires when the connection drops before the "close" event
      source.onerror = () => {
        if (sourceRef.current !== source) return;
        source.close();
        sourceRef.current = null;
        setError("Connection to the API lost. Is the backend running?");
        setStatus("error");
      };
    },
    [closeStream]
  );

  const stop = useCallback(() => {
    if (!sourceRef.current) return;
    closeStream();
    setStatus("stopped");
  }, [closeStream]);

  // Close the stream when the component is unmounted
  useEffect(() => closeStream, [closeStream]);

  return { results, status, error, total, scanId, start, stop };
}