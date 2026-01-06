import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

@Injectable({
    providedIn: 'root'
})
export class SparqlService {

    constructor(private api: ApiService) { }

    query(sparql: string): Observable<{ head: { vars: string[] }, results: { bindings: any[] } }> {
        return this.api.get<{ head: { vars: string[] }, results: { bindings: any[] } }>('/api/sparql', { query: sparql });
    }
}
