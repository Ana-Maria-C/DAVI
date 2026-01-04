import os
import time
import pyoxigraph

class RDFStore:
    _instance = None
    _store = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RDFStore()
        return cls._instance
    
    def __init__(self):
        if RDFStore._instance is not None:
             raise Exception("This class is a singleton!")
        self._store = pyoxigraph.Store()
        self.graph_path = self._resolve_graph_path()

    def _resolve_graph_path(self):
        base_dir = os.path.dirname(os.path.abspath(__file__)) 
        backend_dir = os.path.dirname(base_dir) 
        project_root = os.path.dirname(backend_dir) 
        return os.path.join(project_root, "data", "movielens_graph.ttl")

    def load_data(self):
        """Loads the RDF data if it exists."""
        if os.path.exists(self.graph_path):
            file_size = os.path.getsize(self.graph_path)
            if file_size == 0:
                print("WARNING: RDF file is empty.")
                return

            print(f"Loading RDF data from {self.graph_path}...")
            start_time = time.time()
            try:
                with open(self.graph_path, "rb") as f:
                    self._store.load(f, "text/turtle", base_iri="http://example.org/movielens/")
                print(f"Data loaded in {time.time() - start_time:.2f}s")
                print(f"Total Triples: {len(self._store)}")
            except Exception as e:
                print(f"FAILED to load RDF data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"WARNING: Data file not found at {self.graph_path}")

    @property
    def store(self):
        return self._store

rdf_store = RDFStore.get_instance()
