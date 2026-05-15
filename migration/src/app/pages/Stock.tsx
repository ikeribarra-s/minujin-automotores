import { useState, useEffect, useRef } from "react";
import { Car, Upload } from "lucide-react";
import { toast } from "sonner";
import { api, uploadFile, parseDecimal } from "../api";
import type { Vehiculo } from "../api";
import { formatCurrency } from "../lib/utils";
import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import Input from "../components/Input";
import Select from "../components/Select";
import Textarea from "../components/Textarea";
import Modal from "../components/Modal";

const emptyVehiculo = {
  marca: '',
  modelo: '',
  anio: new Date().getFullYear(),
  version: '',
  color: '',
  kilometraje: 0,
  tipo: 'usado' as const,
  procedencia: 'compra' as const,
  patente: '',
  precio_compra: '',
  precio_venta: '',
  observaciones: '',
};

export default function Stock() {
  const [activeTab, setActiveTab] = useState<'lista' | 'agregar' | 'foto'>('lista');
  const [vehiculos, setVehiculos] = useState<Vehiculo[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('todos');
  const [editingVehiculo, setEditingVehiculo] = useState<Vehiculo | null>(null);
  const [deletingVehiculo, setDeletingVehiculo] = useState<Vehiculo | null>(null);
  const [nuevoVehiculo, setNuevoVehiculo] = useState(emptyVehiculo);
  const [saving, setSaving] = useState(false);
  const [fotoVehiculoId, setFotoVehiculoId] = useState('');
  const [fotoFile, setFotoFile] = useState<File | null>(null);
  const [editFotoFile, setEditFotoFile] = useState<File | null>(null);
  const [uploadingFoto, setUploadingFoto] = useState(false);
  const fotoInputRef = useRef<HTMLInputElement>(null);
  const editFotoInputRef = useRef<HTMLInputElement>(null);

  const loadVehiculos = () =>
    api
      .get('/vehiculos/')
      .then(setVehiculos)
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false));

  useEffect(() => { loadVehiculos(); }, []);

  const filteredVehiculos = vehiculos.filter((v) =>
    filter === 'todos' ? true : v.estado === filter
  );

  const disponibles = vehiculos.filter((v) => v.estado === 'disponible').length;
  const reservados = vehiculos.filter((v) => v.estado === 'reservado').length;
  const vendidos = vehiculos.filter((v) => v.estado === 'vendido').length;

  const handleAgregarVehiculo = async () => {
    if (!nuevoVehiculo.marca || !nuevoVehiculo.modelo) {
      toast.error('Marca y modelo son obligatorios');
      return;
    }
    setSaving(true);
    try {
      const created = await api.post('/vehiculos/', {
        marca: nuevoVehiculo.marca,
        modelo: nuevoVehiculo.modelo,
        anio: nuevoVehiculo.anio,
        version: nuevoVehiculo.version || undefined,
        color: nuevoVehiculo.color || undefined,
        kilometraje: nuevoVehiculo.kilometraje,
        tipo: nuevoVehiculo.tipo,
        procedencia: nuevoVehiculo.procedencia,
        patente: nuevoVehiculo.patente || undefined,
        precio_compra: nuevoVehiculo.precio_compra ? parseFloat(nuevoVehiculo.precio_compra) : undefined,
        precio_venta: nuevoVehiculo.precio_venta ? parseFloat(nuevoVehiculo.precio_venta) : undefined,
        observaciones: nuevoVehiculo.observaciones || undefined,
      }) as Vehiculo;
      setVehiculos((prev) => [created, ...prev]);
      setNuevoVehiculo(emptyVehiculo);
      setActiveTab('lista');
      toast.success('Vehículo agregado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!editingVehiculo) return;
    setSaving(true);
    try {
      const { id, created_at, updated_at, fecha_ingreso, foto_url, ...rest } = editingVehiculo;
      const updated = await api.put(`/vehiculos/${id}`, {
        ...rest,
        precio_compra: rest.precio_compra ? parseFloat(rest.precio_compra) : null,
        precio_venta: rest.precio_venta ? parseFloat(rest.precio_venta) : null,
      }) as Vehiculo;

      let final = updated;
      if (editFotoFile) {
        final = await uploadFile(`/vehiculos/${id}/foto`, editFotoFile) as Vehiculo;
      }
      setVehiculos((prev) => prev.map((v) => (v.id === id ? final : v)));
      setEditingVehiculo(null);
      setEditFotoFile(null);
      toast.success('Vehículo actualizado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteVehiculo = async () => {
    if (!deletingVehiculo) return;
    setSaving(true);
    try {
      await api.delete(`/vehiculos/${deletingVehiculo.id}`);
      setVehiculos((prev) => prev.filter((v) => v.id !== deletingVehiculo.id));
      setDeletingVehiculo(null);
      toast.success('Vehículo eliminado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleReserva = async (vehiculo: Vehiculo) => {
    const nuevoEstado = vehiculo.estado === 'disponible' ? 'reservado' : 'disponible';
    try {
      const { id, created_at, updated_at, fecha_ingreso, foto_url, ...rest } = vehiculo;
      const updated = await api.put(`/vehiculos/${id}`, {
        ...rest,
        precio_compra: rest.precio_compra ? parseFloat(rest.precio_compra) : null,
        precio_venta: rest.precio_venta ? parseFloat(rest.precio_venta) : null,
        estado: nuevoEstado,
      }) as Vehiculo;
      setVehiculos((prev) => prev.map((v) => (v.id === id ? updated : v)));
      toast.success(nuevoEstado === 'reservado' ? 'Vehículo reservado' : 'Vehículo liberado');
    } catch (e: any) {
      toast.error(e.message);
    }
  };

  const handleUploadFoto = async () => {
    if (!fotoFile || !fotoVehiculoId) return;
    setUploadingFoto(true);
    try {
      const updated = await uploadFile(`/vehiculos/${fotoVehiculoId}/foto`, fotoFile) as Vehiculo;
      setVehiculos((prev) => prev.map((v) => (v.id === updated.id ? updated : v)));
      toast.success('Foto actualizada');
      setFotoFile(null);
      setFotoVehiculoId('');
      if (fotoInputRef.current) fotoInputRef.current.value = '';
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setUploadingFoto(false);
    }
  };

  const selectedFotoVehiculo = vehiculos.find((v) => v.id === parseInt(fotoVehiculoId));

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Stock de Vehículos</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden animate-pulse">
              <div className="bg-gray-200 h-36" />
              <div className="p-4 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4" />
                <div className="h-4 bg-gray-200 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Stock de Vehículos</h1>

      <div className="border-b border-gray-200">
        <div className="flex gap-6">
          {(['lista', 'agregar', 'foto'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 border-b-2 font-medium capitalize transition-colors ${
                activeTab === tab
                  ? 'border-[#FF6B2B] text-[#FF6B2B]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab === 'lista' ? 'Lista' : tab === 'agregar' ? 'Agregar' : 'Foto'}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'lista' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
              <p className="text-sm text-gray-500">Total</p>
              <p className="text-2xl font-bold text-gray-900">{vehiculos.length}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
              <p className="text-sm text-gray-500">Disponibles</p>
              <p className="text-2xl font-bold text-green-600">{disponibles}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
              <p className="text-sm text-gray-500">Reservados</p>
              <p className="text-2xl font-bold text-amber-600">{reservados}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-4">
              <p className="text-sm text-gray-500">Vendidos</p>
              <p className="text-2xl font-bold text-gray-600">{vendidos}</p>
            </div>
          </div>

          <Select
            options={[
              { value: 'todos', label: 'Todos' },
              { value: 'disponible', label: 'Disponible' },
              { value: 'reservado', label: 'Reservado' },
              { value: 'vendido', label: 'Vendido' },
            ]}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="max-w-xs"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVehiculos.map((vehiculo) => (
              <div key={vehiculo.id} className="space-y-3">
                <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                  <div className="bg-gray-100 flex items-center justify-center" style={{ height: '148px' }}>
                    {vehiculo.foto_url ? (
                      <img
                        src={vehiculo.foto_url}
                        alt={`${vehiculo.marca} ${vehiculo.modelo}`}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Car className="w-16 h-16 text-gray-400" />
                    )}
                  </div>
                  <div className="p-4 space-y-2">
                    <h3 className="font-bold text-gray-900 tracking-tight">
                      {vehiculo.marca.toUpperCase()} {vehiculo.modelo.toUpperCase()} {vehiculo.version} #{vehiculo.id}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {vehiculo.anio} · {vehiculo.patente ?? 'Sin patente'} · {vehiculo.kilometraje.toLocaleString()} km
                    </p>
                    <div className="flex items-center justify-between">
                      <p className="text-lg font-bold text-gray-900 tracking-tight">
                        {formatCurrency(parseDecimal(vehiculo.precio_venta))}
                      </p>
                      <StatusBadge status={vehiculo.estado} />
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="secondary" className="flex-1" onClick={() => { setEditingVehiculo(vehiculo); setEditFotoFile(null); }}>
                    Editar
                  </Button>
                  {vehiculo.estado !== 'vendido' && (
                    <Button
                      variant={vehiculo.estado === 'disponible' ? 'secondary' : 'secondary'}
                      className={`flex-1 ${vehiculo.estado === 'reservado' ? 'text-amber-700 border-amber-300 hover:bg-amber-50' : ''}`}
                      onClick={() => handleToggleReserva(vehiculo)}
                    >
                      {vehiculo.estado === 'disponible' ? 'Reservar' : 'Liberar'}
                    </Button>
                  )}
                  {vehiculo.estado === 'disponible' && (
                    <Button variant="danger" className="flex-1" onClick={() => setDeletingVehiculo(vehiculo)}>
                      Eliminar
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'agregar' && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Input label="Marca" value={nuevoVehiculo.marca} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, marca: e.target.value })} required />
            <Input label="Modelo" value={nuevoVehiculo.modelo} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, modelo: e.target.value })} required />
            <Input label="Año" type="number" value={nuevoVehiculo.anio} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, anio: parseInt(e.target.value) })} required />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Input label="Versión" value={nuevoVehiculo.version} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, version: e.target.value })} />
            <Input label="Color" value={nuevoVehiculo.color} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, color: e.target.value })} />
            <Input label="Kilometraje" type="number" value={nuevoVehiculo.kilometraje} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, kilometraje: parseInt(e.target.value) || 0 })} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <Select label="Tipo" options={[{ value: 'usado', label: 'Usado' }, { value: 'cero_km', label: 'Cero KM' }]} value={nuevoVehiculo.tipo} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, tipo: e.target.value as 'usado' | 'cero_km' })} />
            <Select label="Procedencia" options={[{ value: 'compra', label: 'Compra' }, { value: 'permuta', label: 'Permuta' }, { value: 'consignacion', label: 'Consignación' }]} value={nuevoVehiculo.procedencia} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, procedencia: e.target.value as 'compra' | 'permuta' | 'consignacion' })} />
            <Input label="Patente" value={nuevoVehiculo.patente} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, patente: e.target.value })} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Input label="Precio compra" type="number" value={nuevoVehiculo.precio_compra} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, precio_compra: e.target.value })} />
            <Input label="Precio venta" type="number" value={nuevoVehiculo.precio_venta} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, precio_venta: e.target.value })} />
          </div>
          <Textarea label="Observaciones" value={nuevoVehiculo.observaciones} onChange={(e) => setNuevoVehiculo({ ...nuevoVehiculo, observaciones: e.target.value })} className="mb-4" />
          <Button variant="primary" onClick={handleAgregarVehiculo} className="w-full" disabled={saving}>
            {saving ? 'Guardando...' : 'Guardar vehículo'}
          </Button>
        </div>
      )}

      {activeTab === 'foto' && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 space-y-4">
          <div className="flex gap-2">
            <Input
              label="ID del vehículo"
              type="number"
              value={fotoVehiculoId}
              onChange={(e) => setFotoVehiculoId(e.target.value)}
              className="flex-1"
            />
          </div>

          {fotoVehiculoId && !selectedFotoVehiculo && (
            <p className="text-red-600">Vehículo no encontrado</p>
          )}

          {selectedFotoVehiculo && (
            <div className="space-y-4">
              <div className="bg-gray-100 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">
                  {selectedFotoVehiculo.marca} {selectedFotoVehiculo.modelo} — Foto actual:
                </p>
                {selectedFotoVehiculo.foto_url ? (
                  <img src={selectedFotoVehiculo.foto_url} alt="Vehículo" className="rounded-lg max-w-sm" />
                ) : (
                  <p className="text-gray-500">Sin foto cargada</p>
                )}
              </div>

              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-600 mb-2">Subir / reemplazar foto</p>
                <input
                  ref={fotoInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  id="foto-upload"
                  onChange={(e) => setFotoFile(e.target.files?.[0] ?? null)}
                />
                <label htmlFor="foto-upload">
                  <Button variant="secondary" className="cursor-pointer">
                    Seleccionar archivo
                  </Button>
                </label>
                {fotoFile && <p className="text-sm text-gray-600 mt-2">{fotoFile.name}</p>}
              </div>

              <Button variant="primary" className="w-full" onClick={handleUploadFoto} disabled={!fotoFile || uploadingFoto}>
                {uploadingFoto ? 'Subiendo...' : 'Subir foto'}
              </Button>
            </div>
          )}
        </div>
      )}

      {editingVehiculo && (
        <Modal isOpen={true} onClose={() => setEditingVehiculo(null)} title="Editar vehículo">
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-600 mb-2">
                {editFotoFile ? editFotoFile.name : 'Reemplazar foto (opcional)'}
              </p>
              <input
                ref={editFotoInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                id="edit-foto-upload"
                onChange={(e) => setEditFotoFile(e.target.files?.[0] ?? null)}
              />
              <label htmlFor="edit-foto-upload">
                <Button variant="secondary" className="mt-2 cursor-pointer">
                  Seleccionar archivo
                </Button>
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input label="Marca" value={editingVehiculo.marca} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, marca: e.target.value })} required />
              <Input label="Modelo" value={editingVehiculo.modelo} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, modelo: e.target.value })} required />
              <Input label="Año" type="number" value={editingVehiculo.anio} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, anio: parseInt(e.target.value) })} required />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input label="Versión" value={editingVehiculo.version ?? ''} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, version: e.target.value || null })} />
              <Input label="Color" value={editingVehiculo.color ?? ''} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, color: e.target.value || null })} />
              <Input label="Kilometraje" type="number" value={editingVehiculo.kilometraje} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, kilometraje: parseInt(e.target.value) || 0 })} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Select label="Tipo" options={[{ value: 'usado', label: 'Usado' }, { value: 'cero_km', label: 'Cero KM' }]} value={editingVehiculo.tipo} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, tipo: e.target.value as 'usado' | 'cero_km' })} />
              <Select label="Procedencia" options={[{ value: 'compra', label: 'Compra' }, { value: 'permuta', label: 'Permuta' }, { value: 'consignacion', label: 'Consignación' }]} value={editingVehiculo.procedencia} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, procedencia: e.target.value as 'compra' | 'permuta' | 'consignacion' })} />
              <Input label="Patente" value={editingVehiculo.patente ?? ''} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, patente: e.target.value || null })} />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input label="Precio compra" type="number" value={editingVehiculo.precio_compra ?? ''} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, precio_compra: e.target.value || null })} />
              <Input label="Precio venta" type="number" value={editingVehiculo.precio_venta ?? ''} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, precio_venta: e.target.value || null })} />
              <Select label="Estado" options={[{ value: 'disponible', label: 'Disponible' }, { value: 'reservado', label: 'Reservado' }, { value: 'vendido', label: 'Vendido' }]} value={editingVehiculo.estado} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, estado: e.target.value as 'disponible' | 'reservado' | 'vendido' })} />
            </div>
            <Textarea label="Observaciones" value={editingVehiculo.observaciones ?? ''} onChange={(e) => setEditingVehiculo({ ...editingVehiculo, observaciones: e.target.value || null })} />
            <div className="flex gap-3 pt-4">
              <Button variant="primary" onClick={handleSaveEdit} className="flex-1" disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar cambios'}
              </Button>
              <Button variant="secondary" onClick={() => setEditingVehiculo(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {deletingVehiculo && (
        <Modal isOpen={true} onClose={() => setDeletingVehiculo(null)} title="¿Eliminar vehículo?" className="max-w-md">
          <div className="space-y-4">
            <p className="text-gray-700">
              ¿Eliminar {deletingVehiculo.marca} {deletingVehiculo.modelo} {deletingVehiculo.anio} (ID {deletingVehiculo.id})?
            </p>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
              <p className="text-sm text-amber-800">Esta acción no se puede deshacer. Falla si el vehículo está vendido o reservado.</p>
            </div>
            <div className="flex gap-3">
              <Button variant="danger" onClick={handleDeleteVehiculo} className="flex-1" disabled={saving}>
                {saving ? 'Eliminando...' : 'Sí, eliminar'}
              </Button>
              <Button variant="secondary" onClick={() => setDeletingVehiculo(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
