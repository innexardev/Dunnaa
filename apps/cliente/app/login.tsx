import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { Redirect, useRouter } from "expo-router";

import { useAuth } from "@/contexts/AuthContext";
import { ApiError, api } from "@/lib/api";

export default function LoginScreen() {
  const router = useRouter();
  const { signIn, user } = useAuth();
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (user) return <Redirect href="/(tabs)" />;

  async function handleSendCode() {
    setError("");
    setLoading(true);
    try {
      const normalized = phone.startsWith("+") ? phone : `+55${phone.replace(/\D/g, "")}`;
      await api.auth.sendCode(normalized);
      setPhone(normalized);
      setStep("code");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Erro ao enviar código");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerify() {
    setError("");
    setLoading(true);
    try {
      const data = await api.auth.verify(phone, code);
      signIn(data.user);
      router.replace("/(tabs)");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Código inválido");
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.card}>
        <Text style={styles.brand}>DUNNAA</Text>
        <Text style={styles.subtitle}>Agende seu corte com facilidade</Text>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        {step === "phone" ? (
          <>
            <Text style={styles.label}>Telefone</Text>
            <TextInput
              style={styles.input}
              placeholder="+5511999999999"
              keyboardType="phone-pad"
              value={phone}
              onChangeText={setPhone}
            />
            <Pressable style={styles.button} onPress={handleSendCode} disabled={loading}>
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Enviar código SMS</Text>
              )}
            </Pressable>
          </>
        ) : (
          <>
            <Text style={styles.label}>Código SMS</Text>
            <TextInput
              style={styles.input}
              placeholder="123456"
              keyboardType="number-pad"
              maxLength={6}
              value={code}
              onChangeText={setCode}
            />
            <Text style={styles.hint}>Enviado para {phone}</Text>
            <Pressable style={styles.button} onPress={handleVerify} disabled={loading}>
              {loading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Entrar</Text>
              )}
            </Pressable>
            <Pressable onPress={() => setStep("phone")}>
              <Text style={styles.link}>Voltar</Text>
            </Pressable>
          </>
        )}
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", backgroundColor: "#f5f5f5", padding: 24 },
  card: { backgroundColor: "#fff", borderRadius: 16, padding: 24 },
  brand: { fontSize: 28, fontWeight: "700", color: "#16a34a", textAlign: "center" },
  subtitle: { fontSize: 14, color: "#666", textAlign: "center", marginTop: 4, marginBottom: 24 },
  label: { fontSize: 14, fontWeight: "600", marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 16,
  },
  button: {
    backgroundColor: "#16a34a",
    borderRadius: 8,
    padding: 14,
    alignItems: "center",
  },
  buttonText: { color: "#fff", fontWeight: "600", fontSize: 16 },
  error: { color: "#dc2626", marginBottom: 12, fontSize: 14 },
  hint: { fontSize: 12, color: "#888", marginBottom: 16 },
  link: { color: "#16a34a", textAlign: "center", marginTop: 16 },
});
