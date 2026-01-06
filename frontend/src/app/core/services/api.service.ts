import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    constructor(private http: HttpClient) { }

    get<T>(endpoint: string, params?: any): Observable<T> {
        return this.http.get<T>(endpoint, { params });
    }

    post<T>(endpoint: string, data: any): Observable<T> {
        return this.http.post<T>(endpoint, data);
    }
}
