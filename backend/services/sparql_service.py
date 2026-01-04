from typing import Any, Dict, Optional, Union
import pyoxigraph
from fastapi import Response
from .rdf_store import rdf_store

class SparqlService:
    def __init__(self):
        self.store = rdf_store.store

    def execute_query(self, query: str) -> Union[Dict[str, Any], Response]:
        try:
            results = self.store.query(query)
            
            if isinstance(results, pyoxigraph.QuerySolutions):
                vars_list = [v.value for v in results.variables]
                bindings = []
                for solution in results:
                    row = {}
                    for var in results.variables:
                        term = solution[var]
                        if term:
                            row[var.value] = {
                                "type": "uri" if isinstance(term, pyoxigraph.NamedNode) else "literal",
                                "value": term.value
                            }
                    bindings.append(row)
                
                return {
                    "head": {"vars": vars_list},
                    "results": {"bindings": bindings}
                }
            
            elif isinstance(results, bool):
                return {"boolean": results}
                
            else:
                return Response(content="Graph results not implemented in JSON yet", status_code=501)

        except Exception as e:
            raise Exception(f"Query Execution Error: {str(e)}")

sparql_service = SparqlService()
