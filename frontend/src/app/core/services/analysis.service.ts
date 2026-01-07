import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface FacetData {
    genres: {
        categories: { [key: string]: string[] };
        other: string[];
    };
    yearRange: { min: number; max: number };
    ratingRange: { min: number; max: number };
}

export interface FilterState {
    genre?: string;
    yearMin?: number;
    yearMax?: number;
    ratingMin?: number;
    ratingMax?: number;
}

@Injectable({
    providedIn: 'root'
})
export class AnalysisService {

    private activeFiltersSubject = new BehaviorSubject<FilterState>({});
    public activeFilters$ = this.activeFiltersSubject.asObservable();

    constructor(private api: ApiService) { }

    getFacets(): Observable<FacetData> {
        return this.api.get<FacetData>('/api/analysis/facets');
    }

    updateFilters(filters: FilterState) {
        this.activeFiltersSubject.next(filters);
    }

    getCurrentFilters(): FilterState {
        return this.activeFiltersSubject.value;
    }

    clearFilters() {
        this.activeFiltersSubject.next({});
    }
}
