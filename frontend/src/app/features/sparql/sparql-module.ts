import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Needed for ngModel

import { SparqlRoutingModule } from './sparql-routing.module';
import { SparqlConsoleComponent } from './pages/sparql-console/sparql-console.component';
import { SharedModule } from '../../shared/shared.module';


@NgModule({
  declarations: [
    SparqlConsoleComponent
  ],
  imports: [
    CommonModule,
    SparqlRoutingModule,
    SharedModule,
    FormsModule
  ]
})
export class SparqlModule { }
