import axios from "axios";
export function errorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again.",
): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail))
      return detail
        .map((item: { msg?: string }) => item.msg || "Invalid input")
        .join(". ");
    if (!error.response)
      return "We couldn’t reach the server. Check your connection and try again.";
  }
  return fallback;
}
export function normalizeUrl(input: string): string {
  const value = input.trim();
  const url = new URL(
    /^[a-z][a-z\d+.-]*:/i.test(value) ? value : `https://${value}`,
  );
  if (
    !["http:", "https:"].includes(url.protocol) ||
    !url.hostname.includes(".") ||
    url.username ||
    url.password
  )
    throw new Error(
      "Enter a valid public website URL, such as https://example.com.",
    );
  return url.href;
}
export function downloadFile(
  name: string,
  content: string,
  type = "application/json",
) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
