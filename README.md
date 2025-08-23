# FreeLytics

Le marché des freelances data est compétitif et sophistiqué.
Afin de se positionner au mieux, les freelances ont besoin de connaître les tendances du marché.
Freelytics vise à fournir les tendances par rôle data en terme de tjm, compétences recherchées, anciennetés requises,...

## A propos

Je suis Thomas, j'ai plus de 6 ans d'expérience dans la data.

## Techno

 - Scrapy pour le scraping
 - Airflow pour l'orchestration
 - Duckdb et ducklake pour le data lake
 - docker pour la containerisation
 - pytest pour les tests unitaires et d'integration
 - ruff

### Scraping

Les données sont scrapées depuis freework[https://www.free-work.com/fr/tech-it].
Le module de scraping est codé dans src/scrapy_freework. Il repose sur le module scrapy pour sa simplicité et sa mise en oeuvre rapide.
Pour une liste de rôle donné, un URL est créé. Cet URL correspond à ce que l'on obtiendrait en faisant une recherche sur le site pour un rôle donné.
On scrap ensuite chaque annonce, sur chaque page. Des détails supplémentaires sont récupérés sur les fiches de chaque annonce.
Une logique de retry est mise en place notamment en cas d'erreur 429. Un délai de plus en plus long est appliqué afin de ne pas être bloqué par le site.

### Orchestration

Un DAG journalier airflow permet d'automatiser le scraping. Une fois le csv créé, on le transforme en parquet.
A terme, j'utiliserai une step fonction aws pour scraper et stocker les parquet sur S3.
