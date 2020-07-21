
CREATE TABLE public.article_tags (
    article_url text,
    tag text,

    FOREIGN KEY (article_url) REFERENCES public.articles(url) ON DELETE CASCADE
);