import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    constructor(private http: HttpClient) { }

    get(endpoint: string, params?: any): Observable<any> {
        return this.http.get(endpoint, { params });
    }

    post(endpoint: string, data: any): Observable<any> {
        return this.http.post(endpoint, data);
    }
}
