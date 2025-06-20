SET SQL_SAFE_UPDATES = 0;
USE spacenews_db;

-- 1. List all articles
SELECT *
FROM news_articles_table;

-- 2. Find articles with “SpaceX” in the title
SELECT id, title, url
FROM news_articles_table
WHERE title LIKE '%SpaceX%';

-- 3. Recent posts by a specific author (convert “Month Day, Year” → DATE)
SELECT id,
       title,
       `date`
FROM publishing_info
WHERE author = 'Alice Smith'
ORDER BY STR_TO_DATE(`date`, '%M %e, %Y') DESC;

-- 4. Full article details (title, author, date, excerpt)
SELECT n.id,
       n.title,
       p.author,
       p.`date`,
       n.postexcerpt
FROM news_articles_table AS n
JOIN publishing_info   AS p
  ON n.id = p.id;

-- 5. Article count per author
SELECT p.author,
       COUNT(*) AS article_count
FROM publishing_info AS p
JOIN news_articles_table AS n
  ON p.id = n.id
GROUP BY p.author;

-- 6. Average content length per author
SELECT p.author,
       AVG(CHAR_LENGTH(n.content)) AS avg_content_len
FROM publishing_info AS p
JOIN news_articles_table AS n
  ON p.id = n.id
GROUP BY p.author;

-- 7. Top 3 authors by article count (window function)
SELECT author,
       article_count
FROM (
  SELECT p.author,
         COUNT(*) AS article_count,
         RANK() OVER (ORDER BY COUNT(*) DESC) AS rk
  FROM publishing_info AS p
  JOIN news_articles_table AS n
    ON p.id = n.id
  GROUP BY p.author
) AS ranked
WHERE rk <= 3;

-- 8. Populate missing excerpts
UPDATE news_articles_table
SET postexcerpt = LEFT(content, 150)
WHERE postexcerpt IS NULL OR postexcerpt = '';

-- 9. Delete orphan articles (no publishing info)
DELETE n
FROM news_articles_table AS n
LEFT JOIN publishing_info AS p
  ON n.id = p.id
WHERE p.id IS NULL;

-- 10a. Remove articles published before 2020-01-01
DELETE n
FROM news_articles_table AS n
JOIN publishing_info AS p
  ON n.id = p.id
WHERE STR_TO_DATE(p.`date`, '%M %e, %Y') < '2020-01-01';

-- 10b. Remove corresponding publishing records
DELETE
FROM publishing_info
WHERE STR_TO_DATE(`date`, '%M %e, %Y') < '2020-01-01';
