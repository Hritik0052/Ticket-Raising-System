document.addEventListener("DOMContentLoaded", function () {
    const departmentSelect = document.getElementById("department");
    const subDepartmentSelect = document.getElementById("sub_department");

    if (!departmentSelect || !subDepartmentSelect) {
        console.error("Dropdowns not found in DOM.");
        return;
    }

    departmentSelect.addEventListener("change", function () {
        let deptId = this.value;

        fetch(`/accounts/get-subdepartments/${deptId}/`)
            .then(response => response.json())
            .then(data => {
                // Reset options
                subDepartmentSelect.innerHTML = '<option value="" disabled selected>Choose a sub-department</option>';

                // Populate with response data
                data.sub_departments.forEach(sub => {
                    let option = document.createElement("option");
                    option.value = sub.id;
                    option.textContent = sub.name;
                    subDepartmentSelect.appendChild(option);
                });
            })
            .catch(error => console.error("Error fetching sub-departments:", error));
    });
});
