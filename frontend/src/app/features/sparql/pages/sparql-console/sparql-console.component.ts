import { Component } from '@angular/core';
import { SparqlService } from '../../../../core/services/sparql.service';

@Component({
    selector: 'app-sparql-console',
    standalone: false,
    templateUrl: './sparql-console.html',
    styleUrls: ['./sparql-console.scss']
})
export class SparqlConsoleComponent {
    query = `SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10`;
    columns: string[] = [];
    results: any[] = [];
    isLoading = false;
    error: string | null = null;
    rawResponse: any = null;
    showRawJson = false;

    constructor(private sparqlService: SparqlService) { }

    executeQuery() {
        this.isLoading = true;
        this.error = null;
        this.columns = [];
        this.results = [];

        this.sparqlService.query(this.query).subscribe({
            next: (res) => {
                console.log('SPARQL Response:', res);
                this.rawResponse = res;
                if (res.head && res.head.vars) {
                    this.columns = res.head.vars;
                    this.results = res.results.bindings;
                }
                this.isLoading = false;
            },
            error: (err) => {
                console.error('SPARQL Error:', err);
                this.error = err.message || 'An error occurred while executing the query.';
                this.isLoading = false;
            }
        });
    }
}
