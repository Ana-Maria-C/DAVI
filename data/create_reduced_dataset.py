import rdflib
from rdflib import Graph, URIRef
import os
import random

def create_reduced_dataset(input_file, output_file, movie_limit=50):
    print(f"Loading graph from {input_file}...")
    g = Graph()
    g.parse(input_file, format="ttl")
    print(f"Graph loaded. Total triples: {len(g)}")

    ml = rdflib.Namespace("http://example.org/movielens/")
    rdf = rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    print(f"Selecting {movie_limit} random movies...")
    # Find all movies
    all_movies = list(g.subjects(rdf.type, ml.Movie))
    
    if len(all_movies) > movie_limit:
        selected_movies = random.sample(all_movies, movie_limit)
    else:
        selected_movies = all_movies
    
    selected_movies_set = set(selected_movies)
    print(f"Selected {len(selected_movies)} movies.")

    new_g = Graph()
    
    # Bind namespaces
    for prefix, namespace in g.namespaces():
        new_g.bind(prefix, namespace)

    print("Constructing new graph...")
    
    # 1. Add all triples for the selected movies
    for movie in selected_movies:
        for p, o in g.predicate_objects(movie):
            new_g.add((movie, p, o))

    # 2. Add all Genres (keep all genres to be safe, they are small)
    for s in g.subjects(rdf.type, ml.Genre):
        for p, o in g.predicate_objects(s):
            new_g.add((s, p, o))

    # 3. Add Ratings for the selected movies AND the users who rated them
    # Iterate over all ratings. If ratingOf is a selected movie, keep it and the user.
    # Note: Scanning all ratings might be slow if there are many. 
    # Better approach might be to find ratings specifically.
    # But usually Rating nodes are subjects. We need to find triples like:
    # ?rating ml:ratingOf ?movie
    
    count = 0
    users_to_include = set()

    for s, p, o in g.triples((None, ml.ratingOf, None)):
        if o in selected_movies_set:
            # s is the Rating node
            # Add all triples for this Rating node
            for rp, ro in g.predicate_objects(s):
                new_g.add((s, rp, ro))
                if rp == ml.ratedBy:
                    users_to_include.add(ro)
            # Ensure type definition is added
            new_g.add((s, rdf.type, ml.Rating))

    print(f"Included {len(users_to_include)} users referenced by ratings.")

    # 4. Add the User triples for users referenced
    for user in users_to_include:
        for p, o in g.predicate_objects(user):
            new_g.add((user, p, o))
        # Ensure type definition is added
        new_g.add((user, rdf.type, ml.User))
    
    print(f"Saving reduced graph to {output_file}...")
    new_g.serialize(destination=output_file, format="ttl")
    print(f"Done. Reduced graph has {len(new_g)} triples.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(current_dir, "movielens_graph.ttl")
    output_path = os.path.join(current_dir, "movielens_graph_reduced.ttl")
    
    create_reduced_dataset(input_path, output_path, movie_limit=50)
