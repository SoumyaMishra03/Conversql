SELECT *
FROM space_news
WHERE "article id" = 3001;

SELECT "article id", "headline", "publication date", "news source"
FROM space_news
WHERE "publication date" >= '2025-01-01';

SELECT "article id", "headline", "views count", "likes"
FROM space_news
WHERE "reader engagement" > 1000;

SELECT COUNT(*) AS articles_per_source, "news source"
FROM space_news
GROUP BY "news source";

SELECT "article id", "headline", "shares", "comments"
FROM (
    SELECT "article id", "headline", "shares", "comments",
           RANK() OVER (ORDER BY "views count" DESC) AS view_rank
    FROM space_news
) AS ranked
WHERE view_rank <= 5;

UPDATE space_news
SET "summary" = 'Updated summary content'
WHERE "article id" = 3002;

DELETE FROM space_news
WHERE "likes" < 10;
