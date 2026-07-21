export default defineEventHandler(async () => {
  const config = useRuntimeConfig()

  try {
    const data = await $fetch(
      "https://api.themoviedb.org/3/movie/popular",
      {
        headers: {
          Authorization: `Bearer ${config.tmdbToken}`,
          Accept: "application/json",
        },

        query: {
          language: "vi-VN",
          page: 1,
        },
      }
    )

    return data
  } catch (error) {
    console.error(error)

    throw createError({
      statusCode: 500,
      statusMessage: "Không thể lấy dữ liệu TMDB",
    })
  }
})