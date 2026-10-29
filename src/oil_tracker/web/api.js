// The only way the web talks to Python: the local HTTP API (architecture.md).
const token = new URLSearchParams(location.search).get("token") ?? "";

async function send(method, path, body) {
  const headers = { "X-OLT-Token": token };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  return fetch(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
}

async function asJson(response) {
  const text = await response.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return { error: text || response.statusText };
  }
}

/** { ok, status, data } for every JSON call; callers decide what a status means. */
export async function call(method, path, body) {
  const response = await send(method, path, body);
  return { ok: response.ok, status: response.status, data: await asJson(response) };
}

export async function getJson(path) {
  const result = await call("GET", path);
  if (!result.ok) throw new Error(result.data.error ?? `HTTP ${result.status}`);
  return result.data;
}

/** An image as an ImageBitmap, with the response headers. */
export async function getImage(path) {
  const response = await send("GET", path);
  if (!response.ok) throw new Error((await asJson(response)).error ?? `HTTP ${response.status}`);
  return { bitmap: await createImageBitmap(await response.blob()), headers: response.headers };
}
