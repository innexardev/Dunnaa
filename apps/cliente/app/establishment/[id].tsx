import type { Establishment, Service, StaffMember } from "@dunnaa/shared";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { ApiError, api } from "@/lib/api";

export default function EstablishmentScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [est, setEst] = useState<Establishment | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);

  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        const [e, s, st] = await Promise.all([
          api.establishments.get(id),
          api.establishments.services(id),
          api.establishments.staff(id),
        ]);
        setEst(e);
        setServices(s.filter((x) => x.active));
        setStaff(st.filter((x) => x.active));
      } catch (e) {
        Alert.alert("Erro", e instanceof ApiError ? e.message : "Falha ao carregar");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  async function handleBook(service: Service, staffMember: StaffMember) {
    if (!id) return;
    setBooking(true);
    try {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const dateStr = tomorrow.toISOString().slice(0, 10);
      const avail = await api.availability(id, staffMember.id, service.id, dateStr);
      const slot = avail.slots[0];
      if (!slot) {
        Alert.alert("Sem horários", "Nenhum horário disponível amanhã.");
        return;
      }
      await api.appointments.create({
        establishment_id: id,
        service_id: service.id,
        staff_id: staffMember.id,
        scheduled_at: slot.start_at,
        payment_type: "single",
      });
      Alert.alert("Agendado!", "Seu horário foi reservado.", [
        { text: "OK", onPress: () => router.push("/(tabs)/appointments") },
      ]);
    } catch (e) {
      Alert.alert("Erro", e instanceof ApiError ? e.message : "Falha ao agendar");
    } finally {
      setBooking(false);
    }
  }

  async function handleJoinQueue() {
    if (!id) return;
    try {
      await api.queue.join(id);
      Alert.alert("Fila", "Você entrou na fila!", [
        { text: "OK", onPress: () => router.push("/(tabs)/queue") },
      ]);
    } catch (e) {
      Alert.alert("Erro", e instanceof ApiError ? e.message : "Falha ao entrar na fila");
    }
  }

  if (loading || !est) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#16a34a" />
      </View>
    );
  }

  const firstStaff = staff[0];

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.name}>{est.name}</Text>
      <Text style={styles.meta}>
        {est.address} — {est.city}, {est.state}
      </Text>

      {est.queue_mode_enabled && (
        <Pressable style={styles.queueBtn} onPress={handleJoinQueue}>
          <Text style={styles.queueBtnText}>Entrar na fila virtual</Text>
        </Pressable>
      )}

      <Text style={styles.section}>Serviços</Text>
      {services.map((service) => (
        <View key={service.id} style={styles.card}>
          <Text style={styles.serviceName}>{service.name}</Text>
          <Text style={styles.price}>
            R$ {service.price.toFixed(2)} · {service.duration_minutes} min
          </Text>
          {firstStaff && (
            <Pressable
              style={styles.bookBtn}
              disabled={booking}
              onPress={() => handleBook(service, firstStaff)}
            >
              <Text style={styles.bookBtnText}>
                {booking ? "Agendando..." : `Agendar com ${firstStaff.name}`}
              </Text>
            </Pressable>
          )}
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fafafa" },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  name: { fontSize: 24, fontWeight: "700" },
  meta: { fontSize: 14, color: "#666", marginTop: 4, marginBottom: 16 },
  section: { fontSize: 18, fontWeight: "600", marginTop: 16, marginBottom: 8 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#eee",
  },
  serviceName: { fontSize: 16, fontWeight: "600" },
  price: { fontSize: 14, color: "#666", marginTop: 4 },
  bookBtn: {
    marginTop: 12,
    backgroundColor: "#16a34a",
    borderRadius: 8,
    padding: 10,
    alignItems: "center",
  },
  bookBtnText: { color: "#fff", fontWeight: "600" },
  queueBtn: {
    backgroundColor: "#15803d",
    borderRadius: 8,
    padding: 14,
    alignItems: "center",
    marginBottom: 8,
  },
  queueBtnText: { color: "#fff", fontWeight: "600" },
});
