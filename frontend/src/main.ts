import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter, RouterOutlet, Routes, ActivatedRoute, Router, RouterLink } from '@angular/router';
import { provideHttpClient, HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

const API = 'http://localhost:8000/api';

type Establishment = {
  id: number;
  name: string;
  slug: string;
  email?: string;
  auto_confirm?: boolean;
  interval_minutes?: number;
  simultaneous_capacity?: number;
};

type Service = { id: number; name: string; duration_minutes: number; color: string; establishment: number };
type Slot = { start: string; end: string };
type Availability = { id: number; establishment: number; weekday: number; start_time: string; end_time: string };
type Appointment = {
  id: number;
  establishment: number;
  service: number;
  start_datetime: string;
  end_datetime: string;
  status: 'pending' | 'confirmed' | 'cancelled';
  client_name: string;
  client_phone: string;
};

type AdminMe = { is_superuser: boolean; establishments: Establishment[] };

@Component({
  selector: 'home-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <main class="public-page">
      <section class="hero">
        <p class="kicker">CitaFlow</p>
        <h1>Selecciona un negocio</h1>
        <p class="subtitle">Reserva cita o entra al panel de administración.</p>
      </section>

      <section class="panel panel-wide" style="margin-top:12px;">
        <div class="panel-head">
          <h2>Negocios disponibles</h2>
          <a routerLink="/admin/login" class="btn-secondary">Administración</a>
        </div>
        <div class="business-grid">
          <a class="business-card" *ngFor="let e of establishments" [routerLink]="['/', e.slug]">
            <h3>{{ e.name }}</h3>
            <p>/{{ e.slug }}</p>
          </a>
        </div>
      </section>
    </main>
  `,
})
class HomePageComponent {
  private readonly http = inject(HttpClient);
  establishments: Establishment[] = [];

  constructor() {
    this.http.get<Establishment[]>(`${API}/establishments`).subscribe((r) => (this.establishments = r));
  }
}

@Component({
  selector: 'public-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <main class="public-page">
      <div class="top-nav">
        <a routerLink="/" class="btn-secondary">Inicio</a>
        <a routerLink="/admin/login" class="btn-secondary">Administración</a>
      </div>

      <section class="hero">
        <p class="kicker">CitaFlow</p>
        <h1>Reserva tu cita en minutos</h1>
        <p class="subtitle">Negocio: <strong>{{ slug }}</strong></p>
      </section>

      <section class="booking-grid">
        <article class="panel">
          <h2>1. Servicio</h2>
          <select class="input" [(ngModel)]="serviceId" (change)="onServiceChange()">
            <option value="" disabled>Selecciona un servicio</option>
            <option *ngFor="let s of services" [value]="s.id">{{ s.name }} ({{ s.duration_minutes }} min)</option>
          </select>
        </article>

        <article class="panel">
          <h2>2. Fecha</h2>
          <input class="input" type="date" [(ngModel)]="date" (change)="loadSlots()" />
        </article>

        <article class="panel panel-wide">
          <div class="panel-head">
            <h2>3. Hora</h2>
            <span class="status" *ngIf="loadingSlots">Cargando...</span>
          </div>

          <div class="slots" *ngIf="slots.length > 0">
            <button type="button" class="slot" *ngFor="let sl of slots" [class.slot-active]="selectedStart === sl.start" (click)="selectedStart = sl.start">
              {{ sl.start | date : 'shortTime' }}
            </button>
          </div>

          <p class="hint" *ngIf="!loadingSlots && date && slots.length === 0">No hay huecos para esa fecha.</p>
        </article>

        <article class="panel panel-wide">
          <h2>4. Tus datos</h2>
          <div class="form-row">
            <input class="input" placeholder="Nombre" [(ngModel)]="clientName" />
            <input class="input" placeholder="Teléfono" [(ngModel)]="clientPhone" />
          </div>

          <button type="button" class="btn-primary" [disabled]="isBookingDisabled" (click)="book()">
            {{ booking ? 'Reservando...' : 'Confirmar reserva' }}
          </button>

          <p class="message success" *ngIf="messageType === 'success'">{{ message }}</p>
          <p class="message error" *ngIf="messageType === 'error'">{{ message }}</p>
        </article>
      </section>
    </main>
  `,
})
class PublicPageComponent {
  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);

  slug = 'demo';
  services: Service[] = [];
  slots: Slot[] = [];
  serviceId = '';
  date = '';
  selectedStart = '';
  clientName = '';
  clientPhone = '';
  loadingSlots = false;
  booking = false;
  message = '';
  messageType: 'success' | 'error' | '' = '';

  get isBookingDisabled() {
    return this.booking || !this.serviceId || !this.selectedStart || !this.clientName.trim() || !this.clientPhone.trim();
  }

  constructor() {
    this.route.paramMap.subscribe((params) => {
      this.slug = params.get('slug') || 'demo';
      this.loadServices();
    });
  }

  loadServices() {
    this.http.get<Service[]>(`${API}/${this.slug}/services`).subscribe((r) => {
      this.services = r;
      if (r.length > 0) this.serviceId = String(r[0].id);
    });
  }

  onServiceChange() {
    this.selectedStart = '';
    if (this.date) this.loadSlots();
  }

  loadSlots() {
    if (!this.serviceId || !this.date) {
      this.slots = [];
      return;
    }

    this.loadingSlots = true;
    this.selectedStart = '';

    this.http.get<Slot[]>(`${API}/${this.slug}/availability?date=${this.date}&service_id=${this.serviceId}`).subscribe({
      next: (r) => {
        this.slots = r;
        this.loadingSlots = false;
      },
      error: () => {
        this.loadingSlots = false;
        this.message = 'No se pudo cargar disponibilidad.';
        this.messageType = 'error';
      },
    });
  }

  book() {
    if (this.isBookingDisabled) return;

    this.booking = true;
    this.message = '';
    this.messageType = '';

    this.http.post(`${API}/${this.slug}/appointments`, {
      service: Number(this.serviceId),
      start_datetime: this.selectedStart,
      client_name: this.clientName,
      client_phone: this.clientPhone,
    }).subscribe({
      next: () => {
        this.booking = false;
        this.message = 'Reserva creada correctamente.';
        this.messageType = 'success';
        this.clientName = '';
        this.clientPhone = '';
        this.loadSlots();
      },
      error: () => {
        this.booking = false;
        this.message = 'No se pudo crear la reserva. Prueba otro horario.';
        this.messageType = 'error';
      },
    });
  }
}

@Component({
  selector: 'admin-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <main class="admin-wrap admin-auth">
      <section class="admin-card">
        <div class="top-nav">
          <a routerLink="/" class="btn-secondary">Inicio</a>
        </div>

        <h1>Panel de administración</h1>
        <p class="hint">Accede como dueño/gestor para administrar agenda y servicios.</p>

        <div class="auth-field">
          <label class="auth-label" for="login-username">Usuario</label>
          <input id="login-username" class="input auth-input" placeholder="Usuario" [(ngModel)]="username" />
        </div>

        <div class="auth-field">
          <label class="auth-label" for="login-password">Password</label>
          <input id="login-password" class="input auth-input" type="password" placeholder="Password" [(ngModel)]="password" />
        </div>

        <button class="btn-primary auth-submit" (click)="login()">Entrar</button>
        <p class="message error auth-error" *ngIf="message">{{ message }}</p>
      </section>
    </main>
  `,
})
class AdminLoginComponent {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  username = 'owner_demo';
  password = 'owner_demo';
  message = '';

  login() {
    this.http.post<{ access: string }>(`${API}/auth/login`, { username: this.username, password: this.password }).subscribe({
      next: (r) => {
        localStorage.setItem('token', r.access);
        const headers = new HttpHeaders({ Authorization: `Bearer ${r.access}` });
        this.http.get<AdminMe>(`${API}/admin/me`, { headers }).subscribe({
          next: (me) => {
            localStorage.setItem('admin_role', me.is_superuser ? 'superuser' : 'owner');
            this.router.navigateByUrl('/admin');
          },
          error: () => (this.message = 'No se pudo cargar el perfil de administración'),
        });
      },
      error: () => (this.message = 'Credenciales inválidas'),
    });
  }
}

@Component({
  selector: 'admin-panel',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  template: `
    <main class="admin-wrap">
      <section class="admin-top">
        <h1>Administración <small *ngIf="currentEstablishmentName">- {{ currentEstablishmentName }}</small></h1>
        <div>
          <button class="btn-secondary" (click)="tab='appointments'">Reservas</button>
          <button class="btn-secondary" (click)="tab='services'">Servicios</button>
          <button class="btn-secondary" (click)="tab='availability'">Disponibilidad</button>
          <button class="btn-secondary" (click)="tab='blocks'">Bloqueos</button>
          <button class="btn-secondary" *ngIf="isSuperuser" (click)="tab='businesses'">Negocios</button>
          <button class="btn-secondary" (click)="logout()">Salir</button>
        </div>
      </section>

      <section class="admin-card" *ngIf="isSuperuser">
        <h2>Modo administrador global</h2>
        <select class="input" [(ngModel)]="currentEstablishmentId" (change)="updateCurrentEstablishmentName()">
          <option *ngFor="let e of establishments" [value]="e.id">{{ e.name }} ({{ e.slug }})</option>
        </select>
      </section>

      <section class="admin-card" *ngIf="tab==='appointments'">
        <h2>Reservas</h2>
        <table class="table">
          <thead><tr><th>Cliente</th><th>Inicio</th><th>Estado</th><th></th></tr></thead>
          <tbody>
            <tr *ngFor="let a of appointments">
              <td>{{ a.client_name }}</td>
              <td>{{ a.start_datetime | date:'short' }}</td>
              <td>
                <select class="input" [(ngModel)]="a.status">
                  <option value="pending">pending</option>
                  <option value="confirmed">confirmed</option>
                  <option value="cancelled">cancelled</option>
                </select>
              </td>
              <td><button class="btn-secondary" (click)="updateAppointment(a)">Guardar</button></td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="admin-card" *ngIf="tab==='services'">
        <h2>Servicios</h2>
        <div class="form-row">
          <input class="input" placeholder="Nombre" [(ngModel)]="serviceForm.name" />
          <input class="input" type="number" placeholder="Duración" [(ngModel)]="serviceForm.duration_minutes" />
        </div>
        <div class="form-row">
          <input class="input" placeholder="#Color" [(ngModel)]="serviceForm.color" />
        </div>
        <button class="btn-primary" (click)="saveService()">{{ serviceForm.id ? 'Actualizar' : 'Crear' }} servicio</button>
      </section>

      <section class="admin-card" *ngIf="tab==='availability'">
        <h2>Disponibilidad semanal</h2>
        <p class="hint">Para deshabilitar un día completo, no dejes franjas en ese día.</p>
        <div class="form-row">
          <select class="input" [(ngModel)]="availabilityForm.weekday">
            <option [value]="1">Lunes</option>
            <option [value]="2">Martes</option>
            <option [value]="3">Miércoles</option>
            <option [value]="4">Jueves</option>
            <option [value]="5">Viernes</option>
            <option [value]="6">Sábado</option>
            <option [value]="0">Domingo</option>
          </select>
          <input class="input" type="time" [(ngModel)]="availabilityForm.start_time" />
        </div>
        <div class="form-row">
          <input class="input" type="time" [(ngModel)]="availabilityForm.end_time" />
          <button class="btn-primary" (click)="createAvailability()">Añadir franja</button>
        </div>

        <table class="table">
          <thead><tr><th>Día</th><th>Inicio</th><th>Fin</th><th></th></tr></thead>
          <tbody>
            <tr *ngFor="let av of visibleAvailabilities">
              <td>{{ weekdayLabel(av.weekday) }}</td>
              <td>{{ av.start_time }}</td>
              <td>{{ av.end_time }}</td>
              <td><button class="btn-secondary" (click)="deleteAvailability(av.id)">Quitar</button></td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="admin-card" *ngIf="tab==='blocks'">
        <h2>Bloquear horario</h2>
        <div class="form-row">
          <input class="input" placeholder="Motivo" [(ngModel)]="blockForm.reason" />
        </div>
        <div class="form-row">
          <input class="input" type="datetime-local" [(ngModel)]="blockForm.start_datetime" />
          <input class="input" type="datetime-local" [(ngModel)]="blockForm.end_datetime" />
        </div>
        <button class="btn-primary" (click)="createBlock()">Crear bloqueo</button>
      </section>

      <section class="admin-card" *ngIf="tab==='businesses' && isSuperuser">
        <h2>Crear negocio nuevo</h2>
        <div class="form-row">
          <input class="input" placeholder="Nombre" [(ngModel)]="estForm.name" />
          <input class="input" placeholder="Slug (ej: barberia-norte)" [(ngModel)]="estForm.slug" />
        </div>
        <div class="form-row">
          <input class="input" placeholder="Email" [(ngModel)]="estForm.email" />
          <input class="input" type="number" placeholder="Intervalo (min)" [(ngModel)]="estForm.interval_minutes" />
        </div>
        <div class="form-row">
          <input class="input" type="number" placeholder="Capacidad simultánea" [(ngModel)]="estForm.simultaneous_capacity" />
          <label class="hint" style="display:flex;align-items:center;gap:8px;">
            <input type="checkbox" [(ngModel)]="estForm.auto_confirm" />
            Autoconfirmar reservas
          </label>
        </div>
        <button class="btn-primary" (click)="createEstablishment()">Crear negocio</button>
        <p class="message success" *ngIf="estMessage && !estError">{{ estMessage }}</p>
        <p class="message error" *ngIf="estError">{{ estError }}</p>
      </section>
    </main>
  `,
})
class AdminPanelComponent {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);

  tab: 'appointments' | 'services' | 'blocks' | 'businesses' | 'availability' = 'appointments';
  appointments: Appointment[] = [];
  services: Service[] = [];
  availabilities: Availability[] = [];
  establishments: Establishment[] = [];
  currentEstablishmentId: number | null = null;
  currentEstablishmentName = '';
  isSuperuser = false;

  serviceForm: Partial<Service> = { name: '', duration_minutes: 30, color: '#0f766e' };
  blockForm = { start_datetime: '', end_datetime: '', reason: '' };
  availabilityForm = { weekday: 1, start_time: '09:00', end_time: '17:00' };
  estForm = { name: '', slug: '', email: '', auto_confirm: true, interval_minutes: 30, simultaneous_capacity: 1 };
  estMessage = '';
  estError = '';

  get visibleAvailabilities() {
    if (!this.currentEstablishmentId) return [];
    return this.availabilities.filter((a) => a.establishment === Number(this.currentEstablishmentId));
  }

  constructor() {
    this.loadMeAndData();
  }

  private headers() {
    const token = localStorage.getItem('token');
    if (!token) {
      this.router.navigateByUrl('/admin/login');
      return new HttpHeaders();
    }
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }

  loadMeAndData() {
    this.http.get<AdminMe>(`${API}/admin/me`, { headers: this.headers() }).subscribe({
      next: (me) => {
        this.isSuperuser = me.is_superuser;
        this.establishments = me.establishments;
        if (!me.establishments.length) return;
        this.currentEstablishmentId = me.establishments[0].id;
        this.currentEstablishmentName = me.establishments[0].name;
        this.loadAll();
      },
    });
  }

  updateCurrentEstablishmentName() {
    const e = this.establishments.find((x) => x.id === Number(this.currentEstablishmentId));
    this.currentEstablishmentName = e?.name || '';
  }

  loadAll() {
    this.http.get<Appointment[]>(`${API}/admin/appointments`, { headers: this.headers() }).subscribe((r) => (this.appointments = r));
    this.http.get<Service[]>(`${API}/admin/services/`, { headers: this.headers() }).subscribe((r) => (this.services = r));
    this.http.get<Availability[]>(`${API}/admin/availability/`, { headers: this.headers() }).subscribe((r) => (this.availabilities = r));
  }

  updateAppointment(a: Appointment) {
    this.http.patch(`${API}/admin/appointments/${a.id}`, { status: a.status }, { headers: this.headers() }).subscribe();
  }

  saveService() {
    if (!this.currentEstablishmentId) return;
    const body = {
      name: this.serviceForm.name,
      duration_minutes: Number(this.serviceForm.duration_minutes),
      color: this.serviceForm.color,
      establishment: Number(this.currentEstablishmentId),
    };

    if (this.serviceForm.id) {
      this.http.patch(`${API}/admin/services/${this.serviceForm.id}/`, body, { headers: this.headers() }).subscribe(() => this.loadAll());
      return;
    }

    this.http.post(`${API}/admin/services/`, body, { headers: this.headers() }).subscribe(() => this.loadAll());
  }

  createBlock() {
    if (!this.currentEstablishmentId) return;
    this.http.post(`${API}/admin/blocks`, {
      establishment: Number(this.currentEstablishmentId),
      start_datetime: new Date(this.blockForm.start_datetime).toISOString(),
      end_datetime: new Date(this.blockForm.end_datetime).toISOString(),
      reason: this.blockForm.reason,
    }, { headers: this.headers() }).subscribe();
  }

  createAvailability() {
    if (!this.currentEstablishmentId) return;
    this.http.post(`${API}/admin/availability/`, {
      establishment: Number(this.currentEstablishmentId),
      weekday: Number(this.availabilityForm.weekday),
      start_time: this.availabilityForm.start_time,
      end_time: this.availabilityForm.end_time,
    }, { headers: this.headers() }).subscribe(() => this.loadAll());
  }

  deleteAvailability(id: number) {
    this.http.delete(`${API}/admin/availability/${id}/`, { headers: this.headers() }).subscribe(() => this.loadAll());
  }

  weekdayLabel(n: number) {
    const labels = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
    return labels[n] || `${n}`;
  }

  createEstablishment() {
    this.estMessage = '';
    this.estError = '';

    const payload = {
      name: this.estForm.name,
      slug: this.estForm.slug,
      email: this.estForm.email,
      auto_confirm: this.estForm.auto_confirm,
      interval_minutes: Number(this.estForm.interval_minutes),
      simultaneous_capacity: Number(this.estForm.simultaneous_capacity),
    };

    this.http.post<Establishment>(`${API}/admin/establishments/`, payload, { headers: this.headers() }).subscribe({
      next: (e) => {
        this.estMessage = `Negocio creado. Acceso dueño: owner_${e.slug} / owner_${e.slug}`;
        this.establishments = [...this.establishments, e];
        this.estForm = { name: '', slug: '', email: '', auto_confirm: true, interval_minutes: 30, simultaneous_capacity: 1 };
      },
      error: (err) => {
        this.estError = err?.error?.detail || 'No se pudo crear el negocio';
      },
    });
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('admin_role');
    this.router.navigateByUrl('/admin/login');
  }
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `<router-outlet></router-outlet>`,
})
class AppComponent {}

const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'admin/login', component: AdminLoginComponent },
  { path: 'admin', component: AdminPanelComponent },
  { path: ':slug', component: PublicPageComponent },
  { path: '**', redirectTo: '' },
];

bootstrapApplication(AppComponent, { providers: [provideRouter(routes), provideHttpClient()] });
