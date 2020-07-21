
CREATE TABLE public.entities (
    article_url text,
    entity text,
    type text,
    salience double precision,
    
    FOREIGN KEY (article_url) REFERENCES public.articles(url) ON DELETE CASCADE
);
