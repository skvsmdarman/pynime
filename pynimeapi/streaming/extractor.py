def extract(self, anime_title, season):
    episode_urls = []  # Store the URLs of all episodes
    for episode_number in range(1, total_episodes + 1):
        episode_url = f"https://example.com/{anime_title}/season{season}/episode{episode_number}"  # Modify the URL pattern as per your website
        episode_urls.append(episode_url)

    # Extract streaming URLs for all episodes
    streaming_urls = []
    for episode_url in episode_urls:
        streaming_url = self.extract_episode(episode_url)
        streaming_urls.append(streaming_url)

    return streaming_urls

def extract_episode(self, url):
    url = self.get_embed_url(url)
    parsed_url = yarl.URL(url)
    content_id = parsed_url.query['id']
    next_host = f"https://{parsed_url.host}/"

    if url[:2] == "//":
        url = "https:" + url
        streaming_page = requests.get(url).content
    else:
        streaming_page = requests.get(url).content

    encryption_key, iv, decryption_key = (
        _.group(1) for _ in KEYS_REGEX.finditer(streaming_page)
    )

    component = self.aes_decrypt(
        ENCRYPTED_DATA_REGEX.search(streaming_page).group(1),
        key=encryption_key,
        iv=iv,
    ).decode() + "&id={}&alias={}".format(
        self.aes_encrypt(content_id, key=encryption_key, iv=iv).decode(), content_id
    )

    _, component = component.split("&", 1)

    ajax_response = requests.get(
        next_host + "encrypt-ajax.php?" + component,
        headers={"x-requested-with": "XMLHttpRequest"},
    )
    content = json.loads(
        self.aes_decrypt(ajax_response.json().get('data'), key=decryption_key, iv=iv)
    )

    def yielder():
        for origin in content.get("source"):
            yield {
                "stream_url": origin.get('file'),
                "quality": self.get_quality(origin.get('label', '')),
            }

        for backups in content.get("source_bk"):
            yield {
                "stream_url": backups.get('file'),
                "quality": self.get_quality(backups.get('label', '')),
            }
    result = list(yielder())
    return result
