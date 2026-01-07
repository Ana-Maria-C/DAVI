import pandas as pd
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD, RDFS
import urllib.parse

# Setup Namespaces
MOVIELENS = Namespace("http://example.org/movielens/")
SCHEMA = Namespace("http://schema.org/")

g = Graph()
g.bind("ml", MOVIELENS)
g.bind("schema", SCHEMA)


def sanitize_uri(text):
    """Sanitizes text to be safe for URI usage."""
    return urllib.parse.quote(
        str(text)
        .replace(" ", "_")
        .replace(":", "")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
    )


def convert_csv_to_rdf(csv_path, output_path):
    print(f"Reading {csv_path}...")
    # Read entire CSV (warning: for huge files chunking is better, but 100k rows is fine for memory)
    df = pd.read_csv(csv_path)

    # Track unique entities to avoid creating duplicate triples for static things (like Genres)
    # Ideally, we iterate and build.

    print("Converting to RDF...")

    count = 0
    total = len(df)

    processed_movies = set()
    processed_genres = set()

    for _, row in df.iterrows():
        count += 1
        if count % 10000 == 0:
            print(f"Processed {count}/{total} rows...")

        user_id = row["userId"]
        movie_id = row["movieId"]
        rating_val = row["rating"]
        title = row["title"]
        genres = str(row["genres"]).split("|")

        # URIs
        user_uri = MOVIELENS[f"User/{user_id}"]
        movie_uri = MOVIELENS[f"Movie/{movie_id}"]
        rating_uri = MOVIELENS[f"Rating/{user_id}_{movie_id}"]

        # 1. Define Movie (if not seen)
        if movie_id not in processed_movies:
            g.add((movie_uri, RDF.type, MOVIELENS.Movie))
            g.add((movie_uri, SCHEMA.name, Literal(title, datatype=XSD.string)))
            g.add(
                (movie_uri, MOVIELENS.movieId, Literal(movie_id, datatype=XSD.integer))
            )

            # Genres
            for genre in genres:
                if genre and genre != "(no genres listed)":
                    genre_sanitized = sanitize_uri(genre)
                    genre_uri = MOVIELENS[f"Genre/{genre_sanitized}"]

                    # Define Genre Class if new
                    if genre_sanitized not in processed_genres:
                        g.add((genre_uri, RDF.type, MOVIELENS.Genre))
                        g.add((genre_uri, RDFS.label, Literal(genre)))
                        processed_genres.add(genre_sanitized)

                    g.add((movie_uri, MOVIELENS.hasGenre, genre_uri))

            processed_movies.add(movie_id)

        # 2. Define Rating
        # We assume every row is a unique rating for a user-movie pair
        g.add((rating_uri, RDF.type, MOVIELENS.Rating))
        g.add(
            (rating_uri, MOVIELENS.ratingValue, Literal(rating_val, datatype=XSD.float))
        )
        g.add((rating_uri, MOVIELENS.ratedBy, user_uri))
        g.add((rating_uri, MOVIELENS.ratingOf, movie_uri))

        # 3. Define User (Implicitly via rating, but good to type it)
        g.add((user_uri, RDF.type, MOVIELENS.User))

        # 4. Tags (Optional)
        user_tags = row.get("user_tags")
        if pd.notna(user_tags) and user_tags:
            # Depending on format, user_tags might be a single tag string or list?
            # Based on verifying data, it looks like a string.
            # We can attach it to the movie-user relationship or just the movie?
            # A tag is usually: User -> tags -> Movie.
            # Current Schema simplified: Movie hasTagLabel "tag" (anonymous tagging)
            # OR proper reification. For simplicity let's stick to Movie hasTagLabel for now,
            # or better: Tag object.
            # Let's simple: Movie :hasTagLabel "literal_tag"
            g.add((movie_uri, MOVIELENS.hasTagLabel, Literal(user_tags)))

    print(f"Serialization to {output_path}...")
    g.serialize(destination=output_path, format="turtle")
    print("Done!")


if __name__ == "__main__":
    convert_csv_to_rdf("movie_lens_data.csv", "movielens_graph.ttl")
