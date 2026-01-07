import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';

export interface FilterState {
    genre?: string;
    yearMin?: number;
    yearMax?: number;
    ratingMin?: number;
    ratingMax?: number;
}

export interface FacetData {
    genres: {
        categories: { [key: string]: string[] };
        other: string[];
    };
    yearRange: { min: number; max: number };
    ratingRange: { min: number; max: number };
}

@Injectable({
    providedIn: 'root'
})
export class AnalysisService {
    private apiUrl = 'http://localhost:8000/api/analysis';

    private activeFiltersSubject = new BehaviorSubject<FilterState>({});
    public activeFilters$ = this.activeFiltersSubject.asObservable();

    constructor(private http: HttpClient) { }

    getFacets(): Observable<FacetData> {
        return this.http.get<FacetData>(`${this.apiUrl}/facets`);
    }

    updateFilters(filters: FilterState) {
        this.activeFiltersSubject.next(filters);
    }

    getStatistics(): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/stats`);
    }
}
