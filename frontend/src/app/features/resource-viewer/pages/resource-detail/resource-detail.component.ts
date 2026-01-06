import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { SparqlService } from '../../../../core/services/sparql.service';
import { Observable, map, switchMap, of } from 'rxjs';

@Component({
    selector: 'app-resource-detail',
    standalone: false,
    templateUrl: './resource-detail.html',
    styleUrl: './resource-detail.scss'
})
export class ResourceDetailComponent implements OnInit {
    uri: string | null = null;
    properties$: Observable<{ p: string, o: string, type: string }[]> | null = null;

    constructor(private route: ActivatedRoute, private sparqlService: SparqlService) { }

    ngOnInit() {
        this.route.queryParams.subscribe(params => {
            this.uri = params['uri'];
            if (this.uri) {
                this.loadProperties(this.uri);
            }
        });
    }

    loadProperties(uri: string) {
        const query = `
      SELECT ?p ?o
      WHERE {
        <${uri}> ?p ?o
      }
    `;

        this.properties$ = this.sparqlService.query(query).pipe(
            map(res => res.results.bindings.map(b => ({
                p: b.p.value,
                o: b.o.value,
                type: b.o.type
            })))
        );
    }
}
