import https from "node:https";

const TMDB_HOST = "api.themoviedb.org";
let cachedAddresses: string[] = [];
let cacheExpiresAt = 0;

async function resolveTmdbAddresses(): Promise<string[]> {
  if (cachedAddresses.length && Date.now() < cacheExpiresAt) {
    return cachedAddresses;
  }

  const response = await fetch(
    `https://dns.google/resolve?name=${TMDB_HOST}&type=A`,
    { headers: { Accept: "application/dns-json" } },
  );
  if (!response.ok) {
    throw new Error(`TMDB DNS lookup failed (${response.status})`);
  }
  const data = (await response.json()) as {
    Answer?: Array<{ type: number; data: string }>;
  };
  const addresses = (data.Answer || [])
    .filter((answer) => answer.type === 1)
    .map((answer) => answer.data);
  if (!addresses.length) {
    throw new Error("TMDB DNS lookup returned no IPv4 address");
  }
  cachedAddresses = addresses;
  cacheExpiresAt = Date.now() + 10 * 60 * 1000;
  return addresses;
}

function requestByAddress<T>(
  address: string,
  path: string,
  token: string,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const request = https.request(
      {
        hostname: address,
        port: 443,
        path,
        method: "GET",
        servername: TMDB_HOST,
        headers: {
          Host: TMDB_HOST,
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
        timeout: 12_000,
      },
      (response) => {
        const chunks: Buffer[] = [];
        response.on("data", (chunk) => chunks.push(Buffer.from(chunk)));
        response.on("end", () => {
          const body = Buffer.concat(chunks).toString("utf8");
          if (
            !response.statusCode ||
            response.statusCode < 200 ||
            response.statusCode >= 300
          ) {
            reject(
              new Error(
                `TMDB returned ${response.statusCode}: ${body.slice(0, 200)}`,
              ),
            );
            return;
          }
          try {
            resolve(JSON.parse(body) as T);
          } catch (error) {
            reject(error);
          }
        });
      },
    );
    request.on("timeout", () =>
      request.destroy(new Error("TMDB request timed out")),
    );
    request.on("error", reject);
    request.end();
  });
}

export async function tmdbFetch<T>(
  path: string,
  token: string,
  query: Record<string, string | number> = {},
): Promise<T> {
  const search = new URLSearchParams(
    Object.entries(query).map(([key, value]) => [key, String(value)]),
  );
  const requestPath = `${path}${search.size ? `?${search}` : ""}`;

  try {
    return (await $fetch(`https://${TMDB_HOST}${requestPath}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
      },
    })) as T;
  } catch (directError) {
    const addresses = await resolveTmdbAddresses();
    let lastError: unknown = directError;
    for (const address of addresses) {
      try {
        return await requestByAddress<T>(address, requestPath, token);
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError;
  }
}
