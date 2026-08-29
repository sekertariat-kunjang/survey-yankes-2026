// client-side logic for survey multi-step form with GPS Geofencing (Option B)

document.addEventListener('DOMContentLoaded', function() {
    // Set default date and time to current
    const dateInput = document.getElementById('input_tanggal');
    const timeInput = document.getElementById('input_waktu');
    if (dateInput && timeInput) {
        const now = new Date();
        const dateString = now.toISOString().split('T')[0];
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        dateInput.value = dateString;
        timeInput.value = `${hours}:${minutes}`;
    }

    // Coordinates mapping for 37 Puskesmas in Kediri Regency
    const PUSKESMAS_COORDS = {
        "Mojo": { lat: -7.8949252, lon: 111.9655756 },
        "Ngadi": { lat: -7.94, lon: 111.96 },
        "Semen": { lat: -7.8289773, lon: 111.9794299 },
        "Ngadiluwih": { lat: -7.8916192, lon: 111.99378 },
        "Wonorejo": { lat: -7.925, lon: 112.03 },
        "Kras": { lat: -7.9538746, lon: 111.9621196 },
        "Pelas": { lat: -7.971, lon: 112.04 },
        "Sambi": { lat: -7.913, lon: 112.08 },
        "Blabak": { lat: -7.8628761, lon: 112.0363715 },
        "Wates": { lat: -7.9171115, lon: 112.1285698 },
        "Silir": { lat: -7.92, lon: 112.16 },
        "Ngancar": { lat: -7.9321252, lon: 112.1788666 },
        "Plosoklaten": { lat: -7.8734424, lon: 112.1685302 },
        "Pranggang": { lat: -7.8523965, lon: 112.1706928 },
        "Gurah": { lat: -7.8122286, lon: 112.0772839 },
        "Adan-Adan": { lat: -7.7793569, lon: 112.1242515 },
        "Puncu": { lat: -7.8570205, lon: 112.24051 },
        "Kepung": { lat: -7.809048, lon: 112.2515675 },
        "Keling": { lat: -7.7730812, lon: 112.2517606 },
        "Kandangan": { lat: -7.7498668, lon: 112.2935502 },
        "Bendo": { lat: -7.7626221, lon: 112.1554259 },
        "Sidorejo": { lat: -7.75, lon: 112.195 },
        "Pare": { lat: -7.757672, lon: 112.1809497 },
        "Badas": { lat: -7.7040816, lon: 112.2091357 },
        "Kunjang": { lat: -7.6633252, lon: 112.1511394 },
        "Puhjarak": { lat: -7.7236578, lon: 112.1420779 },
        "Purwosri": { lat: -7.7267, lon: 112.1053 }, // TODO: verify with field data — corrected from duplicate
        "Sumberjo": { lat: -7.8070824, lon: 112.0609852 },
        "Tanon": { lat: -7.81, lon: 112.052 },
        "Pagu": { lat: -7.77072, lon: 112.0856491 },
        "Bangsongan": { lat: -7.7305368, lon: 112.064086 },
        "KayenKidul": { lat: -7.8082, lon: 112.0135 }, // TODO: verify with field data — corrected from duplicate
        "Gampeng": { lat: -7.7694587, lon: 112.0261611 },
        "Ngasem": { lat: -7.798289, lon: 112.0470541 },
        "Tiron": { lat: -7.780692, lon: 111.9551504 },
        "Grogol": { lat: -7.7533636, lon: 111.9736297 },
        "Tarokan": { lat: -7.7172088, lon: 111.9369833 }
    };

    let userLat = null;
    let userLon = null;

    // Haversine formula to compute distance in meters
    function getHaversineDistance(lat1, lon1, lat2, lon2) {
        const R = 6371e3; // Earth radius in meters
        const phi1 = lat1 * Math.PI/180;
        const phi2 = lat2 * Math.PI/180;
        const deltaPhi = (lat2-lat1) * Math.PI/180;
        const deltaLambda = (lon2-lon1) * Math.PI/180;

        const a = Math.sin(deltaPhi/2) * Math.sin(deltaPhi/2) +
                  Math.cos(phi1) * Math.cos(phi2) *
                  Math.sin(deltaLambda/2) * Math.sin(deltaLambda/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        return R * c; // in meters
    }

    // Geolocation detection logic
    function initGeolocation() {
        const card = document.getElementById('gps-status-card');
        const icon = document.getElementById('gps-icon-container');
        const title = document.getElementById('gps-status-title');
        const desc = document.getElementById('gps-status-desc');
        
        // Reset hidden inputs
        document.getElementById('gps_lat').value = '';
        document.getElementById('gps_lon').value = '';
        document.getElementById('gps_distance').value = '';
        document.getElementById('gps_verified').value = '-1';

        title.textContent = "Mendeteksi Lokasi GPS...";
        desc.textContent = "Mohon izinkan akses GPS pada browser Anda.";
        icon.className = "w-10 h-10 rounded-xl bg-slate-200 text-slate-500 flex items-center justify-center text-lg animate-pulse";
        icon.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i>';
        card.className = "bg-slate-50 border border-slate-200 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all";

        if (!navigator.geolocation) {
            title.textContent = "GPS Tidak Didukung";
            desc.textContent = "Browser Anda tidak mendukung layanan lokasi.";
            icon.className = "w-10 h-10 rounded-xl bg-rose-50 text-rose-500 flex items-center justify-center text-lg";
            icon.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i>';
            card.className = "bg-rose-50/50 border border-rose-100 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all";
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLat = position.coords.latitude;
                userLon = position.coords.longitude;
                document.getElementById('gps_lat').value = userLat;
                document.getElementById('gps_lon').value = userLon;

                // Find closest Puskesmas
                let closestPusk = null;
                let minDistance = Infinity;

                for (const [name, coords] of Object.entries(PUSKESMAS_COORDS)) {
                    const dist = getHaversineDistance(userLat, userLon, coords.lat, coords.lon);
                    if (dist < minDistance) {
                        minDistance = dist;
                        closestPusk = name;
                    }
                }

                // If user is within 300 meters of the closest Puskesmas
                if (minDistance <= 300) {
                    document.getElementById('gps_distance').value = Math.round(minDistance);
                    document.getElementById('gps_verified').value = '1';

                    // Highlight and select this Puskesmas
                    const radio = document.querySelector(`input[name="lokasi"][value="Puskesmas ${closestPusk}"]`);
                    if (radio) {
                        radio.checked = true;
                        // Trigger change event to update aesthetics
                        const event = new Event('change');
                        radio.dispatchEvent(event);
                    }

                    title.textContent = "Lokasi GPS Terverifikasi";
                    desc.innerHTML = `Anda terdeteksi di Puskesmas ${closestPusk} (Jarak: ${Math.round(minDistance)}m).<br><span class="text-[10px] text-slate-400 font-mono">GPS Anda: ${userLat.toFixed(6)}, ${userLon.toFixed(6)}</span>`;
                    icon.className = "w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-lg";
                    icon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
                    card.className = "bg-emerald-50/50 border border-emerald-100 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all animate-none";
                } else {
                    // Manual Selection fallback (too far)
                    document.getElementById('gps_verified').value = '0';
                    
                    title.textContent = "Di Luar Area Puskesmas";
                    desc.innerHTML = `Jarak terdekat ke Puskesmas ${closestPusk} adalah ${(minDistance/1000).toFixed(2)} km. Silakan pilih lokasi secara manual.<br><span class="text-[10px] text-slate-400 font-mono">GPS Anda: ${userLat.toFixed(6)}, ${userLon.toFixed(6)}</span>`;
                    icon.className = "w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-lg";
                    icon.innerHTML = '<i class="fa-solid fa-location-dot"></i>';
                    card.className = "bg-amber-50/50 border border-amber-100 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all animate-none";

                    // Update distance if they manually select a Puskesmas
                    updateManualDistance();
                }
            },
            (error) => {
                userLat = null;
                userLon = null;
                document.getElementById('gps_verified').value = '-1';
                
                title.textContent = "GPS Dinonaktifkan";
                desc.textContent = "Gagal mengakses lokasi. Menggunakan mode pemilihan lokasi manual.";
                icon.className = "w-10 h-10 rounded-xl bg-amber-50 text-amber-500 flex items-center justify-center text-lg";
                icon.innerHTML = '<i class="fa-solid fa-circle-question"></i>';
                card.className = "bg-amber-50/50 border border-amber-100 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all animate-none";
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }

    // Dynamic distance calculation for manual selection
    function updateManualDistance() {
        if (userLat === null || userLon === null) return;
        
        const selectedRadio = document.querySelector('input[name="lokasi"]:checked');
        if (selectedRadio) {
            const puskName = selectedRadio.value.replace('Puskesmas ', '');
            const coords = PUSKESMAS_COORDS[puskName];
            
            if (coords) {
                const dist = getHaversineDistance(userLat, userLon, coords.lat, coords.lon);
                document.getElementById('gps_distance').value = Math.round(dist);
                
                const card = document.getElementById('gps-status-card');
                const icon = document.getElementById('gps-icon-container');
                const title = document.getElementById('gps-status-title');
                const desc = document.getElementById('gps-status-desc');
                
                if (dist <= 300) {
                    document.getElementById('gps_verified').value = '1';
                    title.textContent = "Lokasi GPS Terverifikasi";
                    desc.innerHTML = `Anda terdeteksi di Puskesmas ${puskName} (Jarak: ${Math.round(dist)}m).<br><span class="text-[10px] text-slate-400 font-mono">GPS Anda: ${userLat.toFixed(6)}, ${userLon.toFixed(6)}</span>`;
                    icon.className = "w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-lg";
                    icon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
                    card.className = "bg-emerald-50/50 border border-emerald-100 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all";
                } else {
                    document.getElementById('gps_verified').value = '0';
                    title.textContent = "Di Luar Area Puskesmas";
                    desc.innerHTML = `Jarak Anda ke Puskesmas ${puskName} adalah ${(dist/1000).toFixed(2)} km. Pemilihan dilakukan secara manual.<br><span class="text-[10px] text-slate-400 font-mono">GPS Anda: ${userLat.toFixed(6)}, ${userLon.toFixed(6)}</span>`;
                    icon.className = "w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-lg";
                    icon.innerHTML = '<i class="fa-solid fa-location-dot"></i>';
                    card.className = "bg-amber-50/50 border border-amber-100 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 transition-all";
                }
            }
        }
    }

    // Trigger Geolocation on load
    initGeolocation();

    // Bind GPS refresh button
    const refreshBtn = document.getElementById('gps-refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', initGeolocation);
    }

    // Bind radio changes to update distances dynamically in manual mode
    document.querySelectorAll('input[name="lokasi"]').forEach(radio => {
        radio.addEventListener('change', updateManualDistance);
    });

    // Step state tracking
    let currentStep = 1;
    const totalSteps = 5;

    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('surveyForm');

    // Update steps rendering
    function updateSteps() {
        // Hide all steps
        document.querySelectorAll('.step-container').forEach(step => {
            step.classList.remove('active');
        });

        // Show active step
        const activeContainer = document.querySelector(`.step-container[data-step="${currentStep}"]`);
        if (activeContainer) {
            activeContainer.classList.add('active');
            activeContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Update progress indicators
        document.querySelectorAll('.step-lbl').forEach(label => {
            const stepNum = parseInt(label.getAttribute('data-step'));
            const circle = label.querySelector('span');
            
            if (stepNum < currentStep) {
                // Completed
                label.classList.add('text-brand-600');
                circle.className = 'w-6 h-6 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold text-xs border border-brand-200';
                circle.innerHTML = '<i class="fa-solid fa-check text-[10px]"></i>';
            } else if (stepNum === currentStep) {
                // Active
                label.classList.add('text-brand-600');
                circle.className = 'w-6 h-6 rounded-full bg-brand-600 text-white flex items-center justify-center font-bold text-xs shadow-md shadow-brand-500/25';
                circle.innerHTML = stepNum;
            } else {
                // Future
                label.classList.remove('text-brand-600');
                circle.className = 'w-6 h-6 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center font-bold text-xs';
                circle.innerHTML = stepNum;
            }
        });

        // Update progress lines
        document.querySelectorAll('.step-line').forEach(line => {
            const lineNum = parseInt(line.getAttribute('data-line'));
            if (lineNum < currentStep) {
                line.className = 'h-0.5 flex-grow bg-brand-500 mx-2 sm:mx-4 rounded step-line';
            } else {
                line.className = 'h-0.5 flex-grow bg-slate-200 mx-2 sm:mx-4 rounded step-line';
            }
        });

        // Mobile numeric tracker
        const mobileStepCurr = document.getElementById('mobile-step-curr');
        if (mobileStepCurr) {
            mobileStepCurr.textContent = currentStep;
        }

        // Enable/disable buttons
        prevBtn.disabled = (currentStep === 1);
        
        if (currentStep === totalSteps) {
            nextBtn.classList.add('hidden');
            submitBtn.classList.remove('hidden');
        } else {
            nextBtn.classList.remove('hidden');
            submitBtn.classList.add('hidden');
        }
    }

    // Input validations per step
    function validateStep(step) {
        const container = document.querySelector(`.step-container[data-step="${step}"]`);
        if (!container) return true;

        // Check HTML5 validity for inputs in this step
        const inputs = container.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.checkValidity()) {
                input.reportValidity();
                isValid = false;
            }
        });

        if (!isValid) return false;

        // Custom validation: Puskesmas radio list in step 1
        if (step === 1) {
            const locations = container.querySelectorAll('input[name="lokasi"]');
            let isLocChecked = false;
            locations.forEach(loc => {
                if (loc.checked) isLocChecked = true;
            });
            if (!isLocChecked) {
                showAlert('Peringatan', 'Mohon pilih lokasi Puskesmas terlebih dahulu.', 'warning');
                return false;
            }
        }

        return true;
    }

    // Click Next
    nextBtn.addEventListener('click', function() {
        if (validateStep(currentStep)) {
            if (currentStep < totalSteps) {
                currentStep++;
                updateSteps();
            }
        }
    });

    // Click Previous
    prevBtn.addEventListener('click', function() {
        if (currentStep > 1) {
            currentStep--;
            updateSteps();
        }
    });

    // Puskesmas search filter
    const searchInput = document.getElementById('puskesmas-search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase().trim();
            const cards = document.querySelectorAll('#puskesmas-grid label');
            
            cards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Dynamic explanation boxes for Yes/Tidak/Other questions
    document.querySelectorAll('.yn-selector').forEach(radio => {
        // Define function to handle update
        function toggleDetail() {
            const targetId = radio.getAttribute('data-target');
            const detailBox = document.getElementById(targetId);
            if (!detailBox) return;

            const textarea = detailBox.querySelector('textarea');
            const val = radio.value;

            if (radio.checked && (val === 'Tidak' || val === 'Lainnya')) {
                detailBox.classList.remove('hidden');
                if (textarea) textarea.required = true;
            } else if (radio.checked && val === 'Ya') {
                detailBox.classList.add('hidden');
                if (textarea) {
                    textarea.required = false;
                    textarea.value = '';
                }
            }
        }

        // Trigger on load (for initial values)
        toggleDetail();

        // Listen on changes
        const name = radio.getAttribute('name');
        document.querySelectorAll(`input[name="${name}"]`).forEach(sibling => {
            sibling.addEventListener('change', toggleDetail);
        });
    });

    // Checkbox checklist items cosmetic handler
    document.querySelectorAll('.chk-input').forEach(checkbox => {
        function updateStyle() {
            const tile = checkbox.nextElementSibling;
            if (!tile) return;
            const box = tile.querySelector('.checkbox-box');
            
            if (checkbox.checked) {
                box.className = 'mt-0.5 w-4 h-4 shrink-0 rounded border border-brand-600 bg-brand-600 flex items-center justify-center text-[10px] text-white transition-all checkbox-box';
            } else {
                box.className = 'mt-0.5 w-4 h-4 shrink-0 rounded border border-slate-300 bg-white flex items-center justify-center text-[10px] text-transparent transition-all checkbox-box';
            }
        }
        
        updateStyle();
        checkbox.addEventListener('change', updateStyle);
    });

    // Custom alert modal trigger
    function showAlert(title, message, type = 'success') {
        const modal = document.getElementById('alertModal');
        const iconContainer = document.getElementById('alertIconContainer');
        const titleEl = document.getElementById('alertTitle');
        const msgEl = document.getElementById('alertMsg');
        const closeBtn = document.getElementById('alertCloseBtn');

        titleEl.textContent = title;
        msgEl.textContent = message;

        if (type === 'success') {
            iconContainer.className = 'w-16 h-16 rounded-full mx-auto flex items-center justify-center text-2xl mb-4 bg-emerald-100 text-emerald-600';
            iconContainer.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
            closeBtn.className = 'w-full py-3 rounded-xl text-sm font-bold bg-emerald-600 text-white hover:bg-emerald-700 shadow-md transition-all';
        } else if (type === 'error') {
            iconContainer.className = 'w-16 h-16 rounded-full mx-auto flex items-center justify-center text-2xl mb-4 bg-rose-100 text-rose-600';
            iconContainer.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
            closeBtn.className = 'w-full py-3 rounded-xl text-sm font-bold bg-rose-600 text-white hover:bg-rose-700 shadow-md transition-all';
        } else {
            iconContainer.className = 'w-16 h-16 rounded-full mx-auto flex items-center justify-center text-2xl mb-4 bg-amber-100 text-amber-600';
            iconContainer.innerHTML = '<i class="fa-solid fa-exclamation"></i>';
            closeBtn.className = 'w-full py-3 rounded-xl text-sm font-bold bg-amber-600 text-white hover:bg-amber-700 shadow-md transition-all';
        }

        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.remove('opacity-0');
            modal.querySelector('div').classList.remove('scale-95');
        }, 10);
    }

    // Close alert modal
    document.getElementById('alertCloseBtn').addEventListener('click', function() {
        const modal = document.getElementById('alertModal');
        modal.classList.add('opacity-0');
        modal.querySelector('div').classList.add('scale-95');
        setTimeout(() => {
            modal.classList.add('hidden');
            
            // Redirect to dashboard on successful form submit
            if (modal.getAttribute('data-action') === 'redirect') {
                window.location.href = '/dashboard';
            }
        }, 300);
    });

    // Form submission handling via AJAX
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateStep(currentStep)) return;

        // Perform final verification of all steps
        for (let i = 1; i <= totalSteps; i++) {
            if (!validateStep(i)) {
                currentStep = i;
                updateSteps();
                return;
            }
        }

        const formData = new FormData(form);
        const submitButton = document.getElementById('submitBtn');
        const originalText = submitButton.innerHTML;

        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Mengirim...';

        fetch(form.action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;

            if (data.status === 'success') {
                document.getElementById('alertModal').setAttribute('data-action', 'redirect');
                showAlert('Berhasil!', data.message, 'success');
            } else {
                showAlert('Gagal!', data.message || 'Terjadi kesalahan saat menyimpan data.', 'error');
            }
        })
        .catch(error => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
            showAlert('Gagal!', 'Koneksi gagal. Pastikan server aktif.', 'error');
        });
    });

    // Initial state
    updateSteps();
});
