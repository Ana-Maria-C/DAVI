import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SparqlConsoleComponent } from './pages/sparql-console/sparql-console.component';

const routes: Routes = [
    { path: '', component: SparqlConsoleComponent }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class SparqlRoutingModule { }
