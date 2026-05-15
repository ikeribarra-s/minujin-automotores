import { AlertCircle, X } from "lucide-react";
import { useEffect } from "react";

interface ErrorMessageProps {
  message: string;
  onClose: () => void;
}

export default function ErrorMessage({ message, onClose }: ErrorMessageProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-red-50 border border-red-200 rounded-lg shadow-lg px-4 py-3 flex items-center gap-3 max-w-md">
      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
      <p className="text-sm text-red-800 flex-1">{message}</p>
      <button
        onClick={onClose}
        className="text-red-600 hover:text-red-800 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
