import { useState, useEffect, useRef } from "react";
import { Upload, ScanLine, Camera } from "lucide-react";
import { toast } from "sonner";
import { api, uploadFile, parseDecimal } from "../api";
import type { Pagare, ScanResult, VentaLabel } from "../api";
import { formatCurrency, formatDate } from "../lib/utils";
import StatusBadge from "../components/StatusBadge";
import Button from "../components/Button";
import Input from "../components/Input";
import Select from "../components/Select";
import Textarea from "../components/Textarea";
import Modal from "../components/Modal";

interface ScanFormData {
  numero: string;
  monto: string;
  vencimiento: string;
  firmante: string;
  calle: string;
  localidad: string;
  observaciones: string;
  raw_ocr_text: string;
  warning: string | null;
  venta_id: number | null;
}

function scanResultToForm(r: ScanResult): ScanFormData {
  return {
    numero: r.numero ?? '',
    monto: r.monto_numerico ?? '',
    vencimiento: r.fecha_vencimiento ?? '',
    firmante: r.pagador_nombre ?? '',
    calle: '',
    localidad: r.localidad ?? '',
    observaciones: '',
    raw_ocr_text: r.raw_ocr_text,
    warning: r.warning,
    venta_id: null,
  };
}

async function compressImage(file: File, maxWidth = 1920, quality = 0.85): Promise<File> {
  return new Promise((resolve) => {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
      URL.revokeObjectURL(url);
      const scale = Math.min(1, maxWidth / img.width);
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      canvas.getContext('2d')!.drawImage(img, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(
        (blob) => resolve(new File([blob!], file.name.replace(/\.\w+$/, '.jpg'), { type: 'image/jpeg' })),
        'image/jpeg',
        quality
      );
    };
    img.src = url;
  });
}

const emptyPagare = {
  numero: '',
  monto: '',
  vencimiento: '',
  firmante: '',
  calle: '',
  localidad: '',
  venta_id: null as number | null,
};

export default function Pagares() {
  const [activeTab, setActiveTab] = useState<'cartera' | 'escanear' | 'registrar'>('cartera');
  const [pagares, setPagares] = useState<Pagare[]>([]);
  const [ventaLabels, setVentaLabels] = useState<VentaLabel[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('todos');
  const [editingPagare, setEditingPagare] = useState<Pagare | null>(null);
  const [saving, setSaving] = useState(false);

  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [scanningInProgress, setScanningInProgress] = useState(false);
  const [scanForm, setScanForm] = useState<ScanFormData | null>(null);
  const [compressing, setCompressing] = useState(false);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const galleryInputRef = useRef<HTMLInputElement>(null);

  const [nuevoPagare, setNuevoPagare] = useState(emptyPagare);

  useEffect(() => {
    Promise.all([
      api.get('/pagares/'),
      api.get('/ventas/labels'),
    ])
      .then(([p, vl]) => {
        setPagares(p);
        setVentaLabels(vl);
      })
      .catch((e) => toast.error(e.message))
      .finally(() => setLoading(false));
  }, []);

  const ventaOpts = [
    { value: '0', label: 'Sin venta asociada' },
    ...ventaLabels.map((v) => ({ value: v.id.toString(), label: v.label })),
  ];

  const getVentaLabel = (id: number | null) =>
    id ? ventaLabels.find((v) => v.id === id)?.label ?? null : null;

  const filteredPagares = pagares.filter((p) =>
    filter === 'todos' ? true : p.estado === filter
  );

  const handleSaveEdit = async () => {
    if (!editingPagare) return;
    setSaving(true);
    try {
      const updated = await api.patch(`/pagares/${editingPagare.id}`, {
        venta_id: editingPagare.venta_id || undefined,
        numero: editingPagare.numero,
        monto: parseDecimal(editingPagare.monto),
        vencimiento: editingPagare.vencimiento,
        firmante: editingPagare.firmante || undefined,
        calle: editingPagare.calle || undefined,
        localidad: editingPagare.localidad || undefined,
        estado: editingPagare.estado,
        observaciones: editingPagare.observaciones || undefined,
      }) as Pagare;
      setPagares((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      setEditingPagare(null);
      toast.success('Pagaré actualizado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setCompressing(true);
    try {
      const compressed = await compressImage(file);
      setUploadedFile(compressed);
      const reader = new FileReader();
      reader.onload = (event) => setUploadedImage(event.target?.result as string);
      reader.readAsDataURL(compressed);
    } finally {
      setCompressing(false);
    }
  };

  const handleScanDocument = async () => {
    if (!uploadedFile) return;
    setScanningInProgress(true);
    try {
      const result = await uploadFile('/pagares/scan', uploadedFile, 120_000) as ScanResult;
      setScanForm(scanResultToForm(result));
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setScanningInProgress(false);
    }
  };

  const handleGuardarEscaneado = async () => {
    if (!scanForm) return;
    setSaving(true);
    try {
      const created = await api.post('/pagares/', {
        venta_id: scanForm.venta_id || undefined,
        numero: scanForm.numero,
        monto: parseFloat(scanForm.monto) || 0,
        vencimiento: scanForm.vencimiento,
        firmante: scanForm.firmante || undefined,
        calle: scanForm.calle || undefined,
        localidad: scanForm.localidad || undefined,
        observaciones: scanForm.observaciones || undefined,
        raw_ocr_text: scanForm.raw_ocr_text || undefined,
      }) as Pagare;
      setPagares((prev) => [created, ...prev]);
      setUploadedImage(null);
      setUploadedFile(null);
      setScanForm(null);
      setActiveTab('cartera');
      toast.success('Pagaré guardado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleRegistrar = async () => {
    if (!nuevoPagare.numero || !nuevoPagare.monto || !nuevoPagare.vencimiento) {
      toast.error('Número, monto y vencimiento son obligatorios');
      return;
    }
    setSaving(true);
    try {
      const created = await api.post('/pagares/', {
        venta_id: nuevoPagare.venta_id || undefined,
        numero: nuevoPagare.numero,
        monto: parseFloat(nuevoPagare.monto),
        vencimiento: nuevoPagare.vencimiento,
        firmante: nuevoPagare.firmante || undefined,
        calle: nuevoPagare.calle || undefined,
        localidad: nuevoPagare.localidad || undefined,
      }) as Pagare;
      setPagares((prev) => [created, ...prev]);
      setNuevoPagare(emptyPagare);
      setActiveTab('cartera');
      toast.success('Pagaré registrado');
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Cartera de Pagarés</h1>

      <div className="border-b border-gray-200">
        <div className="flex gap-6">
          {([['cartera', 'Cartera'], ['escanear', 'Escanear'], ['registrar', 'Registrar manual']] as const).map(([tab, label]) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 px-1 border-b-2 font-medium transition-colors ${
                activeTab === tab
                  ? 'border-[#FF6B2B] text-[#FF6B2B]'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'cartera' && (
        <div className="space-y-4">
          <Select
            options={[
              { value: 'todos', label: 'Todos' },
              { value: 'pendiente', label: 'Pendiente' },
              { value: 'cobrado', label: 'Cobrado' },
              { value: 'rechazado', label: 'Rechazado' },
            ]}
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="max-w-xs"
          />

          {loading ? (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-200">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="p-4 animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
                  <div className="h-4 bg-gray-200 rounded w-1/4" />
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm divide-y divide-gray-200">
              {filteredPagares.map((pagare) => {
                const ventaLabel = getVentaLabel(pagare.venta_id);
                return (
                  <div key={pagare.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          Pagaré N° {pagare.numero}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {pagare.firmante ?? '—'}
                          {pagare.localidad && ` · ${pagare.localidad}`}
                        </p>
                        {pagare.calle && (
                          <p className="text-xs text-gray-500">{pagare.calle}</p>
                        )}
                        {ventaLabel && (
                          <p className="text-xs text-[#FF6B2B] mt-1 font-medium">{ventaLabel}</p>
                        )}
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">
                          {formatCurrency(parseDecimal(pagare.monto))}
                        </p>
                        <p className="text-sm text-gray-500">Vence: {formatDate(pagare.vencimiento)}</p>
                        <StatusBadge status={pagare.estado} className="mt-2" />
                      </div>
                      <div className="flex justify-end">
                        <Button variant="secondary" onClick={() => setEditingPagare(pagare)}>
                          Editar
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
              {filteredPagares.length === 0 && (
                <div className="p-8 text-center text-gray-500">No hay pagarés registrados</div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'escanear' && (
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Escanear pagaré</h2>
            <p className="text-sm text-gray-600">
              Subí una foto del pagaré. La IA extraerá los datos automáticamente.
            </p>
          </div>

          {!scanForm ? (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 space-y-4">
              <input
                ref={galleryInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                className="hidden"
                onChange={handleImageUpload}
              />
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                className="hidden"
                onChange={handleImageUpload}
              />

              {!uploadedImage ? (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center space-y-4">
                  <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                  <p className="text-sm text-gray-500">Seleccioná una foto del pagaré o tomá una con la cámara</p>
                  <div className="flex gap-3 justify-center flex-wrap">
                    <Button variant="secondary" onClick={() => galleryInputRef.current?.click()}>
                      <Upload className="w-4 h-4 mr-2 inline" />
                      Galería
                    </Button>
                    <Button variant="secondary" onClick={() => cameraInputRef.current?.click()}>
                      <Camera className="w-4 h-4 mr-2 inline" />
                      Tomar foto
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="rounded-lg overflow-hidden border border-gray-200">
                    <img src={uploadedImage} alt="Pagaré escaneado" className="w-full" />
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="primary"
                      onClick={handleScanDocument}
                      disabled={scanningInProgress || compressing}
                      className="flex-1"
                    >
                      {compressing ? (
                        'Comprimiendo imagen...'
                      ) : scanningInProgress ? (
                        <span className="flex items-center justify-center gap-2">
                          <ScanLine className="w-5 h-5 animate-pulse" />
                          Procesando con IA...
                        </span>
                      ) : (
                        'Escanear pagaré'
                      )}
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => { setUploadedImage(null); setUploadedFile(null); }}
                    >
                      Cambiar foto
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800 font-medium">
                  Datos extraídos. Revisá y completá los campos faltantes.
                </p>
              </div>

              {scanForm.warning && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <p className="text-amber-800 text-sm">{scanForm.warning}</p>
                </div>
              )}

              <details className="border border-gray-200 rounded-lg p-4">
                <summary className="cursor-pointer font-medium text-gray-900">Ver OCR completo</summary>
                <pre className="mt-3 text-xs text-gray-600 whitespace-pre-wrap bg-gray-50 p-3 rounded">
                  {scanForm.raw_ocr_text}
                </pre>
              </details>

              <Select
                label="Venta asociada"
                options={ventaOpts}
                value={(scanForm.venta_id ?? 0).toString()}
                onChange={(e) => setScanForm({ ...scanForm, venta_id: parseInt(e.target.value) || null })}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Número (ej: 1/10)"
                  value={scanForm.numero}
                  onChange={(e) => setScanForm({ ...scanForm, numero: e.target.value })}
                />
                <Input
                  label="Monto $"
                  type="number"
                  value={scanForm.monto}
                  onChange={(e) => setScanForm({ ...scanForm, monto: e.target.value })}
                />
              </div>
              <Input
                label="Vencimiento"
                type="date"
                value={scanForm.vencimiento}
                onChange={(e) => setScanForm({ ...scanForm, vencimiento: e.target.value })}
              />
              <Input
                label="Firmante"
                value={scanForm.firmante}
                onChange={(e) => setScanForm({ ...scanForm, firmante: e.target.value })}
              />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Calle"
                  value={scanForm.calle}
                  onChange={(e) => setScanForm({ ...scanForm, calle: e.target.value })}
                />
                <Input
                  label="Localidad"
                  value={scanForm.localidad}
                  onChange={(e) => setScanForm({ ...scanForm, localidad: e.target.value })}
                />
              </div>
              <Textarea
                label="Observaciones"
                value={scanForm.observaciones}
                onChange={(e) => setScanForm({ ...scanForm, observaciones: e.target.value })}
              />
              <div className="flex gap-3">
                <Button variant="primary" onClick={handleGuardarEscaneado} className="flex-1" disabled={saving}>
                  {saving ? 'Guardando...' : 'Guardar pagaré'}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => { setScanForm(null); setUploadedImage(null); setUploadedFile(null); }}
                  className="flex-1"
                >
                  Cancelar
                </Button>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'registrar' && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
          <Select
            label="Venta asociada"
            options={ventaOpts}
            value={(nuevoPagare.venta_id ?? 0).toString()}
            onChange={(e) => setNuevoPagare({ ...nuevoPagare, venta_id: parseInt(e.target.value) || null })}
            className="mb-4"
          />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Input
              label="Número (ej: 1/10)"
              value={nuevoPagare.numero}
              onChange={(e) => setNuevoPagare({ ...nuevoPagare, numero: e.target.value })}
              required
            />
            <Input
              label="Monto"
              type="number"
              value={nuevoPagare.monto}
              onChange={(e) => setNuevoPagare({ ...nuevoPagare, monto: e.target.value })}
              required
            />
          </div>
          <Input
            label="Vencimiento"
            type="date"
            value={nuevoPagare.vencimiento}
            onChange={(e) => setNuevoPagare({ ...nuevoPagare, vencimiento: e.target.value })}
            className="mb-4"
            required
          />
          <Input
            label="Firmante"
            value={nuevoPagare.firmante}
            onChange={(e) => setNuevoPagare({ ...nuevoPagare, firmante: e.target.value })}
            className="mb-4"
          />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <Input
              label="Calle"
              value={nuevoPagare.calle}
              onChange={(e) => setNuevoPagare({ ...nuevoPagare, calle: e.target.value })}
            />
            <Input
              label="Localidad"
              value={nuevoPagare.localidad}
              onChange={(e) => setNuevoPagare({ ...nuevoPagare, localidad: e.target.value })}
            />
          </div>
          <Button variant="primary" onClick={handleRegistrar} className="w-full" disabled={saving}>
            {saving ? 'Registrando...' : 'Registrar pagaré'}
          </Button>
        </div>
      )}

      {editingPagare && (
        <Modal isOpen={true} onClose={() => setEditingPagare(null)} title="Editar pagaré">
          <div className="space-y-4">
            <Select
              label="Venta asociada"
              options={ventaOpts}
              value={(editingPagare.venta_id ?? 0).toString()}
              onChange={(e) => setEditingPagare({ ...editingPagare, venta_id: parseInt(e.target.value) || null })}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Número"
                value={editingPagare.numero}
                onChange={(e) => setEditingPagare({ ...editingPagare, numero: e.target.value })}
              />
              <Input
                label="Monto $"
                type="number"
                value={editingPagare.monto}
                onChange={(e) => setEditingPagare({ ...editingPagare, monto: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Vencimiento"
                type="date"
                value={editingPagare.vencimiento}
                onChange={(e) => setEditingPagare({ ...editingPagare, vencimiento: e.target.value })}
              />
              <Select
                label="Estado"
                options={[
                  { value: 'pendiente', label: 'Pendiente' },
                  { value: 'cobrado', label: 'Cobrado' },
                  { value: 'rechazado', label: 'Rechazado' },
                ]}
                value={editingPagare.estado}
                onChange={(e) => setEditingPagare({ ...editingPagare, estado: e.target.value as Pagare['estado'] })}
              />
            </div>
            <Input
              label="Firmante"
              value={editingPagare.firmante ?? ''}
              onChange={(e) => setEditingPagare({ ...editingPagare, firmante: e.target.value || null })}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Calle"
                value={editingPagare.calle ?? ''}
                onChange={(e) => setEditingPagare({ ...editingPagare, calle: e.target.value || null })}
              />
              <Input
                label="Localidad"
                value={editingPagare.localidad ?? ''}
                onChange={(e) => setEditingPagare({ ...editingPagare, localidad: e.target.value || null })}
              />
            </div>
            <Textarea
              label="Observaciones"
              value={editingPagare.observaciones ?? ''}
              onChange={(e) => setEditingPagare({ ...editingPagare, observaciones: e.target.value || null })}
            />
            <div className="flex gap-3 pt-4">
              <Button variant="primary" onClick={handleSaveEdit} className="flex-1" disabled={saving}>
                {saving ? 'Guardando...' : 'Guardar cambios'}
              </Button>
              <Button variant="secondary" onClick={() => setEditingPagare(null)} className="flex-1">
                Cancelar
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
